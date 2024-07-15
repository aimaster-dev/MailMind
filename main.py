from typing import Union
import os
import pickle
import asyncio
import logging

from fastapi import FastAPI
from starlette.responses import RedirectResponse

from zoho_oauth import generateAuthUrl, getAccessToken, refreshAccessToken
from zoho_client import ZohoClient 
from replier import main as replier

logger = logging.getLogger(__name__)
pickle_path = os.path.join(os.environ['PKL_PATH'], "zoho_tokens.pkl")

store = {}
store_lock = asyncio.Lock()
run_lock = asyncio.Lock()

def refreshAccessTokenFunc():
    global store
    logger.info("store: ", store)
    access_token_res = refreshAccessToken(store['refresh_token'])
    logger.info("refresh_res: ", access_token_res)
    store['access_token'] = access_token_res["access_token"]
    pickle.dump(store, open(pickle_path, "wb"))
    return store['access_token']

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/run")
async def run():
    await run_lock.acquire()
    await store_lock.acquire()
    global store
    try:
        if 'access_token' not in store or 'refresh_token' not in store:
            try:
                store = pickle.load(open("zoho_tokens.pkl", "rb"))
            except (OSError, IOError) as e:
                return RedirectResponse(generateAuthUrl())
        zc = ZohoClient(store['access_token'], refreshAccessTokenFunc)
        replier(zc, lambda : (run_lock.release(), store_lock.release()))
    except Exception as e:
        run_lock.release()
        store_lock.release()
        return {"Error": str(e)}
    return {"Hello": "Ran for 10 (up to) unreads!"}


@app.get("/auth")
def prompt_auth():
    return RedirectResponse(generateAuthUrl())

@app.get("/auth/callback")
async def auth_callback(code: str):
    access_token_res = getAccessToken(code)
    await store_lock.acquire()
    global store
    if 'refresh_token' in access_token_res: 
        store['refresh_token'] = access_token_res["refresh_token"]
    store['access_token'] = access_token_res["access_token"]
    pickle.dump(store, open(pickle_path, "wb"))
    store_lock.release()
    return {"Success": access_token_res}