from zoho_oauth import generateAuthUrl, getAccessToken, refreshAccessToken
from zoho_client import ZohoClient 
import pickle

store = {}

def refreshAccessTokenFunc():
    global store
    access_token_res = refreshAccessToken(store['refresh_token'])
    store['access_token'] = access_token_res["access_token"]
    pickle.dump(store, open("zoho_tokens.pkl", "wb"))
    return store['access_token']

try:
    store = pickle.load(open("zoho_tokens.pkl", "rb"))
except (OSError, IOError) as e:
    pickle.dump(store, open("zoho_tokens.pkl", "wb"))

if 'access_token' not in store or 'refresh_token' not in store:
    print(generateAuthUrl())
    code = input("Enter code: ")
    access_token_res = getAccessToken(code)
    print(access_token_res)
    store['refresh_token'] = access_token_res["refresh_token"]
    store['access_token'] = access_token_res["access_token"]
    pickle.dump(store, open("zoho_tokens.pkl", "wb"))

zc = ZohoClient(store['access_token'], refreshAccessTokenFunc)
# emails = zc.getEmails()
# content = []
# for email in emails:
#     email.update(zc.readEmailContent(email))
#     print(email)
#     print(zc.replyEmail(email, {'subject': 'test reply', 'content': 'test content\n'}, 
#                   schedule={'isSchedule': True, 'scheduleType': 5}))
