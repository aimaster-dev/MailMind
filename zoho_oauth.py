import requests
import os

redirect_uri = os.environ["ZOHO_REDIRECT_URI"]

def generateAuthUrl():
    url = "https://accounts.zoho.com/oauth/v2/auth"
    params = {
        'scope': 'ZohoMail.accounts.READ,ZohoMail.messages.ALL',
        'client_id': os.environ["ZOHO_CLIENT_ID"],
        'response_type': 'code',
        'access_type': 'offline',
        'redirect_uri': redirect_uri,
    }

    return requests.Request('GET', url, params=params).prepare().url

def getAccessToken(code):
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        'code': code,
        'client_id': os.environ["ZOHO_CLIENT_ID"],
        'client_secret': os.environ["ZOHO_CLIENT_SECRET"],
        'redirect_uri': redirect_uri, 
        'scope': 'ZohoMail.accounts.READ,ZohoMail.messages.ALL',
        'grant_type': 'authorization_code',
    }

    return requests.post(url, data=data).json()

def refreshAccessToken(refresh_token):
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        'refresh_token': refresh_token,
        'client_id': os.environ["ZOHO_CLIENT_ID"],
        'client_secret': os.environ["ZOHO_CLIENT_SECRET"],
        'redirect_uri': redirect_uri,
        'grant_type': 'refresh_token',
    }

    return requests.post(url, data=data).json()