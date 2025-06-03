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
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
pickle_path = os.path.join(os.environ['PKL_PATH'], "zoho_tokens.pkl")
print("👉 PKL save path:", pickle_path)

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
    logger.info("start /run api endpoint")
    await run_lock.acquire()
    await store_lock.acquire()
    global store
    try:
        if not store:
            if os.path.exists(pickle_path):
                store.clear()
                store.update(pickle.load(open(pickle_path, "rb")))
                logger.info(f"✅ Loaded token from file: {pickle_path}")
            else:
                run_lock.release()
                store_lock.release()
                return RedirectResponse("/auth")  # ← only if really missing
            
        logger.info(f"store initial info {store}")
        if 'access_token' not in store or 'refresh_token' not in store:
            try:
                store.clear()
                store.update(pickle.load(open(pickle_path, "rb")))  # ✅ use update
                logger.info(f"✅ Loaded token from file: {pickle_path}")
            except (OSError, IOError) as e:
                return RedirectResponse(generateAuthUrl())
        
        logger.info(f"store info: {store['access_token']}, {store['refresh_token']}")
        zc = ZohoClient(store['access_token'], refreshAccessTokenFunc)
        logger.info(f"zc info: {zc}")
        replier(zc, lambda : (run_lock.release(), store_lock.release()))
    except Exception as re:
        print("🔥 Error in replier:", repr(re))
        run_lock.release()
        store_lock.release()
        return {"Error": str(re)}
    return {"Hello": "Ran for 10 (up to) unreads!"}


@app.get("/auth")
def prompt_auth():
    return RedirectResponse(generateAuthUrl())

@app.get("/auth/callback")
async def auth_callback(code: str):
    logger.info(f"Received OAuth code: {code}")
    access_token_res = getAccessToken(code)
    logger.info(f"Access token response: {access_token_res}")
    await store_lock.acquire()
    global store

    try:
        store['access_token'] = access_token_res["access_token"]
        if 'refresh_token' in access_token_res:
            store['refresh_token'] = access_token_res["refresh_token"]

        os.makedirs(os.environ['PKL_PATH'], exist_ok=True)
        with open(pickle_path, "wb") as f:
            pickle.dump(store, f)
            logger.info(f"✅ Saved tokens to: {pickle_path}")

        logger.info(f"✅ Loaded into memory: {store}")
    except Exception as e:
        logger.error(f"❌ Failed to save tokens: {e}")
        return {"error": str(e)}
    finally:
        store_lock.release()

    return {"message": "✅ Auth successful! Now go to http://localhost:8000/run to start."}