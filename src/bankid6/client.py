import os
import requests
from pathlib import Path
from urllib.parse import urljoin

from .handlers import StartParams, BankIdStartResponse
from .message import Messages
from .exceptions import check_bankid_error


BASE_DIR = Path(__file__).resolve().parent

TEST_CERT_PEM = os.path.join(BASE_DIR, 'certs/bankid.crt')
TEST_KEY_PEM = os.path.join(BASE_DIR, 'certs/bankid.key')
TEST_CA_PEM = os.path.join(BASE_DIR, 'certs/testCARootCert.pem')


class BankIdClient(object):

    def __init__(
        self, 
        key_pem=None, 
        cert_pem=None, 
        ca_pem=None, 
        prod_env=False, 
        request_timeout=None,
        messages=Messages,
        is_mobile:bool=True
    ) -> None:

        if prod_env:
            self.api_url = "https://appapi2.bankid.com/rp/v6.0/"

            if not all([key_pem, cert_pem, ca_pem]):
                raise KeyError("Need key_pem, cert_pem and ca_pem files for test environment")
            
            self.key_pem = key_pem
            self.cert_pem = cert_pem
            self.ca_pem = ca_pem

        else:
            self.api_url = "https://appapi2.test.bankid.com/rp/v6.0/"
            self.key_pem = TEST_KEY_PEM
            self.cert_pem = TEST_CERT_PEM
            self.ca_pem = TEST_CA_PEM
        
        self.client = requests.Session()
        self.client.verify = self.ca_pem
        self.client.cert = (self.key_pem, self.cert_pem)
        self.client.headers = {"Content-Type": "application/json"}

        self.timeout = request_timeout
        self.messages = messages
        self.is_mobile = is_mobile
    
    def _uri(self, url):
        return urljoin(self.api_url, url)
    
    def _post(self, uri, json_data):
        response = self.client.post(uri, json=json_data, timeout=self.timeout)
        check_bankid_error(response, self.messages)

        return response
    
    def _initiate_bankid_action(
        self,
        url,
        endUserIp=None,
        personalNumber=None,
        callInitiator=None,
        userVisibleData=None,
        requirement=None,
        userNonVisibleData=None,
        userVisibleDataFormat=None
    ):
        uri = self._uri(url)
        data = StartParams(
            endUserIp=endUserIp,
            personalNumber=personalNumber,
            callInitiator=callInitiator,
            requirement=requirement,
            userVisibleData=userVisibleData,
            userNonVisibleData=userNonVisibleData,
            userVisibleDataFormat=userVisibleDataFormat
        ).clean()

        return self._post(uri, data)

    def auth(
        self, 
        endUserIp, 
        requirement=None, 
        userVisibleData=None, 
        userNonVisibleData=None, 
        userVisibleDataFormat=None
    ):
        response = self._initiate_bankid_action(
            'auth', 
            endUserIp=endUserIp, 
            requirement=requirement, 
            userVisibleData=userVisibleData, 
            userNonVisibleData=userNonVisibleData, 
            userVisibleDataFormat=userVisibleDataFormat
        )

        return BankIdStartResponse(response, self.is_mobile)

    def sign(
        self, 
        endUserIp, 
        userVisibleData, 
        requirement=None, 
        userNonVisibleData=None, 
        userVisibleDataFormat=None
    ):
        response = self._initiate_bankid_action(
            'sign', 
            endUserIp=endUserIp, 
            userVisibleData=userVisibleData, 
            requirement=requirement, 
            userNonVisibleData=userNonVisibleData, 
            userVisibleDataFormat=userVisibleDataFormat
        )

        return BankIdStartResponse(response, self.is_mobile)

    def phone_auth(
        self, 
        personalNumber, 
        callInitiator, 
        requirement=None, 
        userVisibleData=None, 
        userNonVisibleData=None, 
        userVisibleDataFormat=None
    ):
        return self._initiate_bankid_action(
            'phone/auth', 
            personalNumber=personalNumber, 
            callInitiator=callInitiator, 
            requirement=requirement, 
            userVisibleData=userVisibleData, 
            userNonVisibleData=userNonVisibleData, 
            userVisibleDataFormat=userVisibleDataFormat
        )

    def phone_sign(
        self, 
        personalNumber, 
        callInitiator, 
        userVisibleData, 
        requirement=None, 
        userNonVisibleData=None, 
        userVisibleDataFormat=None
    ):
        return self._initiate_bankid_action(
            'phone/sign', 
            personalNumber=personalNumber, 
            callInitiator=callInitiator, 
            userVisibleData=userVisibleData, 
            requirement=requirement, 
            userNonVisibleData=userNonVisibleData, 
            userVisibleDataFormat=userVisibleDataFormat
        )
