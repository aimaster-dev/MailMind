# GPT Zoho Replier

This POC is to try to choose ChatGPT with langchain to try to auto reply emails received from customer service and answer them usiing a predefined set of Q and A messages as best as possible. 

The server integration doesn't fully work with multiple threads due to race condition on global store for access and refresh tokens. (This is just a POC that was hacked up in a day sadly - code is really quite stinky)

**Tech Stack**: LangChain, FastAPI

## Quickstart
- use [devenv](https://devenv.sh) or [poetry](https://python-poetry.org/) to load the dependencies (as per listed in requirements.txt), alternatively use `pip install -r requirements` if you don't want to use any of the package manager.
- initialize the environment variable needed as per indicated in `sample_secrets.txt`
- start the server: `fastapi run`

### Deployment
Dockerfile is included but due to the race condition issue, the program would not work properly with uvicorn worker threads.

## Email Integration
As the test email used is Zoho mail, we used the Zoho API to read new mails and reply them which is not ideal, as gpt generated emails still need reviewing. 

However due to some some limitations on the Zoho API it's impossible to draft new replies without sending them, attempt to use the scheduling feature to mock the draft feature (scheduled x years later) have also not been successful due to some mismatch in Zoho API documentation.

Possible future enhancement is to write it as a full fledged email client instead.

## GPT settings
Q and A messages have embeddings generated using OpenAI's embedding model (text-embedding-ada-002) and stored in ChromaDB for vector search.

For our LLM model we use GPT 3.5 Turbo, which displays similar performance to GPT 4o in the excerpt we generated.

## Receive to Reply Pipeline:
1. Email received as raw data from API
2. send to LLM to summarize as a single question
3. Retrieval Augmented Generation (RAG) to generate context to augment prompt from question
4. Send to LLM with question and prompt to draft up reply

## Further improvements
- Remove the usage of global store to avoid race conditions, replacing with FastAPI's session store
- Generic interface to incorporate multiple email service providers (Or rewrite as full fat email client : TOUGH)
- Package it as a single encapsulated application for easy usage by end users
- Add in type hints for compile time and runtime checks (mypy, beartype)
- Rewrite it in Go Lang cause why not (solve type hints, packaging issue) 

## Acknowledgements
The replier module was referenced from https://gist.github.com/DaveOkpare/172340a50e65a5a895d29b4c5da954dc