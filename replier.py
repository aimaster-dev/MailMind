
import os
import langchain

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA, TransformChain, sequential 
from langchain_community.document_loaders import TextLoader
from langchain.prompts import PromptTemplate

# get from https://platform.openai.com/
# os.environ["OPENAI_API_KEY"] = "<OPENAI_API_KEY>"

# get from https://nla.zapier.com/demo/provider/debug (under User Information, after logging in): 
# os.environ["ZAPIER_NLA_API_KEY"] = "<ZAPIER_NLA_API_KEY>"

def main(zc, endFunc = lambda : None):
    loader = TextLoader(os.path.join(os.environ['RAG_TXT_PATH'], "qa.txt"))
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    docsearch = Chroma.from_documents(texts, embeddings)

    ## step 1. generate retrieval question

    question_template = """Converts this email into a one sentence question. Be concise. Use less than 30 words. Output question in plain text (not JSON).

    Incoming email:
    {input}

    Question:"""

    prompt_template = PromptTemplate(input_variables=["input"], template=question_template)
    question_chain = prompt_template | OpenAI(temperature=.7)


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

    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.as_retriever(), chain_type_kwargs=chain_type_kwargs)

    retrieval = lambda inputs: {"draft_reply": qa.run(inputs["question"])}

    retrieval_chain = TransformChain(input_variables=["question"], output_variables=["draft_reply"], transform=retrieval)

    ## step 3. strip away subject and make sure there's no placeholder
    formatting_template = """Given the following email, strip away the subject line and make sure there's no placeholder in the email content. If there is, replace it with the correct information DON'T LEAVE ANY PLACEHOLDERS OR THE WORLD WOULD IMPLODE. 
    Don't change the meaning of the email content. Remove excessive formalities but still be polite or the world would IMPLODE, MILLIONS WOULD DIE.
    This is the email:
    {input}

    Here is the relevant metadata of the email we are replying to:
    {email_data}

    """
    formatting_chain = PromptTemplate(input_variables=["input", 'email_data'], template=formatting_template) | OpenAI(temperature=.4)


    def schedule_msg(inputs):
        print(inputs)
        return {"zoho_api_data": 
                zc.replyEmail(inputs["email_data"], {
                    "subject": "Re: " + inputs["email_data"]["subject"], 
                    "content": inputs["draft_reply"]
                })}


    # finally, execute

    overall_chain = question_chain | retrieval_chain 
    for (i, email) in enumerate(zc.getEmails()):
        print(f"Email {i+1}:")
        print(email)
        invoked = overall_chain.invoke({'input': email})
        invoked.update({'email_data' :email})
        invoked.update({'draft_reply' : formatting_chain.invoke({'input': invoked['draft_reply'], 'email_data': email})})
        schedule_msg(invoked)
    # content = """
    # Hi,

    # I have missed the gown fitting timeline may I know if it is possible for me to come on the weekends to try and collect the gown?

    # Regards,
    # Jabez Tho
    # """
    # print(overall_chain.invoke({"input": {'subject': 'Enquiry on gown collection', 'content': content}}))
    # print(retrieval_chain.invoke({"question": " Is it possible for me to come on the weekends to try and collect the gown?"}))
    # overall_chain.invoke({"input": " Is it possible for me to come on the weekends to try and collect the gown?"})

    endFunc()