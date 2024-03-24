import os
import requests
from pathlib import Path
from urllib.parse import urljoin

from .handlers import (
    RequestParams, BankIdStartResponse, BankIdPhoneStartResponse, BankIdCollectResponse,
    BankIdCancelResponse
)
from .message import Messages
from .exceptions import check_bankid_error, BankIdValidationError


BASE_DIR = Path(__file__).resolve().parent

TEST_CERT_PEM = os.path.join(BASE_DIR, 'certs/testCert.pem')
TEST_KEY_PEM = os.path.join(BASE_DIR, 'certs/testPrivateKey.pem')
TEST_CA_PEM = os.path.join(BASE_DIR, 'certs/testCARootCert.pem')


class BankIdClient(object):

    def __init__(
            self, key_pem=None, cert_pem=None, ca_pem=None, prod_env=False, request_timeout=None, 
            messages=Messages, is_mobile:bool=False
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
            self.key_pem = key_pem or TEST_KEY_PEM
            self.cert_pem = cert_pem or TEST_CERT_PEM
            self.ca_pem = ca_pem or TEST_CA_PEM
        
        self.client = requests.Session()
        self.client.verify = self.ca_pem
        self.client.cert = (self.cert_pem, self.key_pem)
        self.client.headers = {"Content-Type": "application/json"}

        self.timeout = request_timeout
        self.messages = messages
        self.is_mobile = is_mobile
        self.abs_url = None

        self._update({})
    
    def _uri(self, url):
        return urljoin(self.api_url, url)
    
    def _post(self, uri, json_data):
        response = self.client.post(uri, json=json_data, timeout=self.timeout)
        check_bankid_error(response, self.messages)

        return response
    
    def _update(self, start_response):
        for attr in ['orderRef', 'qrStartToken', 'qrStartSecret', 'order_time']:
            setattr(self, '_' + attr, getattr(start_response, attr, None))
    
    def _initiate_bankid_action(self, url, **kwargs):
        uri = self._uri(url)
        data = RequestParams(**kwargs).clean()

        return self._post(uri, data)

    def auth(
            self, endUserIp, requirement=None, userVisibleData=None, userNonVisibleData=None,
            userVisibleDataFormat=None
        ):
        response = self._initiate_bankid_action(
            'auth', endUserIp=endUserIp, requirement=requirement, userVisibleData=userVisibleData,
            userNonVisibleData=userNonVisibleData, userVisibleDataFormat=userVisibleDataFormat
        )

        start_response = BankIdStartResponse(response, self.is_mobile)
        self._update(start_response)

        return start_response

    def sign(
            self, endUserIp, userVisibleData, requirement=None, userNonVisibleData=None, 
            userVisibleDataFormat=None
        ):
        response = self._initiate_bankid_action(
            'sign', endUserIp=endUserIp, userVisibleData=userVisibleData, requirement=requirement,
            userNonVisibleData=userNonVisibleData, userVisibleDataFormat=userVisibleDataFormat
        )

        start_response = BankIdStartResponse(response, self.is_mobile)
        self._update(start_response)

        return start_response

    def phone_auth(
            self, personalNumber, callInitiator, requirement=None, userVisibleData=None,
            userNonVisibleData=None, userVisibleDataFormat=None
        ):
        response = self._initiate_bankid_action(
            'phone/auth', personalNumber=personalNumber, callInitiator=callInitiator, 
            requirement=requirement, userVisibleData=userVisibleData, 
            userNonVisibleData=userNonVisibleData, userVisibleDataFormat=userVisibleDataFormat
        )

        start_response = BankIdPhoneStartResponse(response)
        self._update(start_response)

        return start_response

    def phone_sign(
            self, personalNumber, callInitiator, userVisibleData, requirement=None, 
            userNonVisibleData=None, userVisibleDataFormat=None
        ):
        response = self._initiate_bankid_action(
            'phone/sign', personalNumber=personalNumber, callInitiator=callInitiator, 
            userVisibleData=userVisibleData, requirement=requirement, 
            userNonVisibleData=userNonVisibleData, userVisibleDataFormat=userVisibleDataFormat
        )

        start_response = BankIdPhoneStartResponse(response)
        self._update(start_response)

        return start_response

    def collect(
            self, orderRef: str=None, qrStartToken: str=None, qrStartSecret: str=None, 
            order_time: int=None
        ):
        uri = self._uri('collect')

        order_ref = orderRef or self._orderRef
        if not order_ref:
            BankIdValidationError("orderRef is empty. Start BankId or give orderRef parameter")

        data = RequestParams(orderRef=order_ref).clean()

        response = self._post(uri, data)

        qr_args = (
            order_time or self._order_time,
            qrStartToken or self._qrStartToken,
            qrStartSecret or self._qrStartSecret
        )
        return BankIdCollectResponse(response, qr_args, self.messages, self.is_mobile)
    
    def cancel(self, orderRef: str=None):
        uri = self._uri('cancel')

        order_ref = orderRef or self._orderRef
        if not order_ref:
            BankIdValidationError("orderRef is empty. Start BankId or give orderRef parameter")
        
        data = RequestParams(orderRef=order_ref).clean()
        
        response = self._post(uri, data)

        return BankIdCancelResponse(response)
