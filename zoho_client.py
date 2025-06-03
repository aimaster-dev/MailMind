import os
import json
import logging
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

api_url = 'https://mail.zoho.com/api/accounts/'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ZohoClient:
    def __init__(self, auth_token, refreshTokenFunc=lambda *args: None):
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f"Zoho-oauthtoken {auth_token}",
            'Content-Type': 'application/json',
        }
        self.refreshTokenFunc = refreshTokenFunc
        self.acct_id, self.acct_addr = self.getAcctDetails()

    def sendAndHandleError(self, func):
        # Handle error once by refreshing token
        resp = func().json()
        logger.debug(resp)
        if (resp['status']['code'] == 404 and resp['data']['errorCode'] == 'INVALID_OAUTHTOKEN'):
            new_auth_token = self.refreshTokenFunc()
            self.headers['Authorization'] = f"Zoho-oauthtoken {new_auth_token}"
            resp = func().json()
        return resp
        
    def getAcctDetails(self):
        payload = self.sendAndHandleError(lambda : session.get(api_url[:-1], headers=self.headers))
        # just take the 1st entry bc not org
        logger.info(payload)
        logger.info(self.headers)
        data = payload['data'][0]
        return ( data['accountId'], data['mailboxAddress'])

    def getEmails(self, start_i=0, counts=10): 
        url = urljoin(api_url, f'{self.acct_id}/messages/view') 
        params = {
            'status': 'unread',
            'start': start_i,
            'limit': counts,
            'includeto': True,

        }
        parsed_resp = self.sendAndHandleError(lambda : session.get(url, params=params, headers=self.headers))
        return parsed_resp['data']

    def searchEmails(self, search_key='newMails'):
        url = urljoin(api_url, f'{self.acct_id}/messages/search') 
        params = {
            'searchKey': search_key,
            'includeto': True,
        }
        parsed_resp = self.sendAndHandleError(lambda : session.get(url, params=params, headers=self.headers))
        return parsed_resp['data']

    def readEmailContent(self, email):
        folder_id = email['folderId']
        msg_id = email['messageId']
        url = urljoin(api_url, f'{self.acct_id}/folders/{folder_id}/messages/{msg_id}/content')
        params = {
            'includeBlockContent' : True            
        }
        parsed_resp = self.sendAndHandleError(lambda : session.get(url, params=params, headers=self.headers))
        return parsed_resp['data']

    def markEmailsRead(self, emails):
        url = urljoin(api_url, f"{self.acct_id}/updatemessage")
        body = {
            "mode": "markAsRead",
            "messageId": [email['messageId'] for email in emails]
        }
        parsed_resp = self.sendAndHandleError(lambda: session.put(url, json=body, headers=self.headers))
        logger.debug(f"Marked emails as read: {parsed_resp}")

    def replyEmail(self, email, reply, schedule=None):
        if schedule is None:
            schedule = {}
        url = urljoin(api_url, f"{self.acct_id}/messages/{email['messageId']}")
        body = {
            'fromAddress': self.acct_addr,
            # intentionally trigger error so not sent
            'toAddress': 'zying1309@gmail.com',
            'subject': reply['subject'],
            'action': 'reply',
            'mode': 'draft',
            'mailFormat': 'plaintext',
            'content': reply['content'] + '\n\n',
        }
        # schedule not working on Zoho side
        # body.update(schedule)
        parsed_resp = self.sendAndHandleError(lambda : session.post(url, json=body, headers=self.headers))
        return parsed_resp 