
import os
import langchain

# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA, TransformChain, sequential 
from langchain_community.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from langchain.schema.messages import AIMessage

def main(zc, endFunc = lambda : None):
    print("✅ replier.main() has been called!")
    print("📥 Zoho client data:", zc.getAcctDetails())
    loader = TextLoader(os.path.join(os.environ['RAG_TXT_PATH'], "qa.txt"))
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    docsearch = Chroma.from_documents(texts, embeddings)

    ## step 1. generate retrieval question

    question_template = """Converts this email into a one sentence question. Be concise. Use less than 30 words. Output question in plain text (not JSON).

    Incoming email:
    {input}

    Question:"""

    prompt_template = PromptTemplate(input_variables=["input"], template=question_template)
    question_chain = prompt_template | ChatOpenAI(model="gpt-4o-mini", temperature=.7)


    ## step 2. draft email from context

    context_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use the answer to write an email.

    {context}

    Question: {question}
    Reply email on enquiry for graduation gown matters as the collection organisation:"""
    PROMPT = PromptTemplate(
        template=context_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-4o-mini"),
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        chain_type_kwargs=chain_type_kwargs
    )

    def retrieval(inputs):
        result = qa.invoke({"query": inputs["question"]})
        if isinstance(result, AIMessage):
            return {"draft_reply": result.content}
        return {"draft_reply": str(result)}

    retrieval_chain = TransformChain(
        input_variables=["question"],
        output_variables=["draft_reply"],
        transform=retrieval
    )

    ## step 3. strip away subject and make sure there's no placeholder
    formatting_template = """Given the following email, strip away the subject line and make sure there's no placeholder in the email content. If there is, replace it with the correct information DON'T LEAVE ANY PLACEHOLDERS OR THE WORLD WOULD IMPLODE. 
    Don't change the meaning of the email content. Remove excessive formalities but still be polite or the world would IMPLODE, MILLIONS WOULD DIE.
    This is the email:
    {input}

    Here is the relevant metadata of the email we are replying to:
    {email_data}

    """
    formatting_chain = PromptTemplate(input_variables=["input", 'email_data'], template=formatting_template) | ChatOpenAI(model="gpt-4o-mini", temperature=.4)


    def schedule_msg(inputs):
        print(inputs)
        return {"zoho_api_data": 
                zc.replyEmail(inputs["email_data"], {
                    "subject": "Re: " + inputs["email_data"]["subject"], 
                    "content": inputs["draft_reply"]
                })}


    # finally, execute

    # overall_chain = question_chain | retrieval_chain 

    for i, email in enumerate(zc.getEmails()):
        print(f"\n📨 Email {i+1}:")
        print(email)

        # Step 1: Generate question + draft reply
        
        # invoked = overall_chain.invoke({'input': email})
        question_output = question_chain.invoke({"input": email})
        print("question_output_message", question_output)
        question_text = question_output.content if isinstance(question_output, AIMessage) else str(question_output)
        print("question_text_message", question_text)
        invoked = retrieval_chain.invoke({"question": question_text})
        print("draft_input_message", invoked)
        # Step 2: Ensure draft_reply is plain string
        draft_reply = invoked.get("draft_reply")
        if isinstance(draft_reply, AIMessage):
            draft_reply = draft_reply.content
        elif not isinstance(draft_reply, str):
            draft_reply = str(draft_reply)
        invoked["draft_reply"] = draft_reply

        # Step 3: Add email data and format final reply
        invoked["email_data"] = email
        draft_input = invoked["draft_reply"]
        print("draft_input_message", invoked["draft_reply"])
        if isinstance(draft_input, AIMessage):
            draft_input = draft_input.content
        elif not isinstance(draft_input, str):
            draft_input = str(draft_input)

        formatted = formatting_chain.invoke({
            "input": draft_input,
            "email_data": email
        })

        # Step 4: Convert formatting output to string
        if isinstance(formatted, AIMessage):
            invoked["draft_reply"] = formatted.content
        else:
            invoked["draft_reply"] = str(formatted)

        # (Optional) Send reply via Zoho
        schedule_msg(invoked)
        zc.markEmailsRead([email])
        # schedule_msg(invoked)  # Uncomment if you want to send it

    endFunc()