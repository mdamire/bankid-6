import pytest
import base64
from datetime import datetime

from bankid6.handlers import (
    RequestParams, BankIdBaseResponse, BankIdStartResponse, BankIdPhoneStartResponse, BankIdCompletionUserData,
    BankIdCompletionDeviceData, BankIdCompletionData, BankIdCollectResponse, BankIdCancelResponse
)
from bankid6 import BankIdValidationError, generate_qr_data
from bankid6.message import get_bankid_collect_message

from .factories import response_factory


class TestRequestParams():
    def _arv(self, func):
        """Assert Raises BankIdValidationError"""
        with pytest.raises(BankIdValidationError):
            func()
    
    def obj(self):
        return RequestParams()
    
    def test_clean_endUserIp(self):
        cldt = RequestParams(endUserIp='192.168.0.1').clean()
        assert cldt['endUserIp'] == '192.168.0.1'

        cldt = RequestParams(endUserIp='2001:0000:130F:0000:0000:09C0:876A:130B').clean()
        assert cldt['endUserIp'] == '2001:0000:130F:0000:0000:09C0:876A:130B'
        
        self._arv(RequestParams(endUserIp='192.168e.0.1').clean)

    def test_clean_userVisibleData(self):
        cldt = RequestParams(userVisibleData='test string').clean()
        assert cldt['userVisibleData'] == base64.b64encode('test string'.encode('utf-8')).decode('utf-8')

        self._arv(RequestParams(userVisibleData='').clean)
    
    def test_clean_userVisibleDataFormat(self):
        cldt = RequestParams(userVisibleDataFormat='simpleMarkdownV1').clean()
        assert cldt['userVisibleDataFormat'] == 'simpleMarkdownV1'
        cldt = RequestParams(userVisibleDataFormat=True).clean()
        assert cldt['userVisibleDataFormat'] == 'simpleMarkdownV1'

        self._arv(RequestParams(userVisibleDataFormat='wrong').clean)
    
    def test_clean_personalNumber(self):
        RequestParams(personalNumber='199002113166').clean()

        self._arv(RequestParams(personalNumber='19900211316a').clean)
        self._arv(RequestParams(personalNumber='9002113166').clean)
    
    def test_clean_callInitiator(self):
        cldt = RequestParams(callInitiator='rp').clean()
        assert cldt['callInitiator'] == 'RP'
        cldt = RequestParams(callInitiator='User').clean()
        assert cldt['callInitiator'] == 'user'

        self._arv(RequestParams(callInitiator='wrong').clean)
    
    def test_requirement(self):
        self._arv(RequestParams(requirement='wrong').clean)
        self._arv(RequestParams(requirement={'wrong': 'value'}).clean)
        self._arv(RequestParams(requirement={'personalNumber':'9002113166'}).clean)

        cldt = RequestParams(requirement={'pinCode': True}).clean()
        assert cldt['requirement'] == {'pinCode': True}
    
    def test_no_exception(self):
        assert RequestParams(order_time='1234').clean()['order_time'] == 1234
        assert RequestParams(orderRef='1234').clean()['orderRef'] == '1234'
        assert RequestParams(qrStartSecret='1234').clean()['qrStartSecret'] == '1234'
        assert RequestParams(qrStartToken='1234').clean()['qrStartToken'] == '1234'
        assert RequestParams(userNonVisibleData='1234').clean().get('userNonVisibleData')

    def test_clean(self):
        cldt = RequestParams(qrStartSecret='1234', order_time='1234', endUserIp='192.168.0.1').clean()
        assert type(cldt) == dict
        assert len(cldt.keys()) == 3
        assert cldt['qrStartSecret'] == '1234'
        assert cldt['order_time'] == 1234
        assert cldt['endUserIp'] == '192.168.0.1'

        cldt = RequestParams(test=None, test1=True).clean()
        assert len(cldt.keys()) == 1
        assert cldt['test1'] == True


class TestResponses():
    def test_BankIdBaseResponse(self):
        obj = BankIdBaseResponse(response=response_factory(200, {"test": True}))
        assert obj.status_code == 200
        assert obj.data == {"test": True}
        assert obj.url == 'test' # default in factory
    
    def test_BankIdStartResponse(self):
        data = {
            'orderRef': '894c311b-0bcb-4d65-bb5b-7580c300f098',
            'autoStartToken': '79439e65-1862-4b27-aefb-dacdb9e62cba',
            'qrStartToken': 'c56e2cd6-c4da-45f1-a104-e59e7cc6d2fa',
            'qrStartSecret': '3cd671e5-3389-4134-9565-decc8388bc8c'
        }
        obj = BankIdStartResponse(response=response_factory(200, data))
        assert obj.orderRef == data['orderRef']
        assert obj.autoStartToken == data['autoStartToken']
        assert obj.qrStartToken == data['qrStartToken']
        assert obj.qrStartSecret == data['qrStartSecret']
        assert type(obj.order_time) == int
        assert obj.launch_url('https://www.google.com') == \
            f'https://app.bankid.com/?autostarttoken={data["autoStartToken"]}&redirect=https%3A%2F%2Fwww.google.com'
        assert obj.qr_data

    def test_BankIdPhoneStartResponse(self):
        data = {
            'orderRef': '894c311b-0bcb-4d65-bb5b-7580c300f098'
        }
        obj = BankIdPhoneStartResponse(response=response_factory(200, data))
        assert isinstance(obj, BankIdBaseResponse)
        assert obj.orderRef == data['orderRef']

    def test_BankIdCollectResponse_incomplete(self):
        data = {
            'orderRef': '00e1b699-1191-43aa-b09d-d95c1bfb4e69', 
            'status': 'pending', 
            'hintCode': 'outstandingTransaction'
        }
        obj = BankIdCollectResponse(response=response_factory(200, data))
        assert obj.orderRef == data['orderRef']
        assert obj.status == data['status']
        assert obj.hintCode == data['hintCode']
        assert obj.message == get_bankid_collect_message(data['status'], data['hintCode'])
        assert obj.qr_data == None
        assert obj.completionData == None

        obj = BankIdCollectResponse(
            response=response_factory(200, data), 
            qr_args=(
                1709667200, 
                'c56e2cd6-c4da-45f1-a104-e59e7cc6d2fa', 
                '3cd671e5-3389-4134-9565-decc8388bc8c'
            )
        )
        assert obj.qr_data

    
    def test_BankIdCollectResponse_complete(self):
        data = {
            'orderRef': '00e1b699-1191-43aa-b09d-d95c1bfb4e69', 
            'status': 'complete', 
            'completionData': {
                'user': {
                    'personalNumber': '197311108711', 
                    'name': 'Jack Sparrow', 
                    'givenName': 'Jack', 
                    'surname': 'Sparrow'
                }, 
                'device': {
                    'ipAddress': '78.66.48.127', 
                    'uhi': 'gjLD+nM+BniMcZyTlPHVg3wu+/eW'
                }, 
                'bankIdIssueDate': '2024-02-12Z', 
                'signature': 'testsig'
            }
        }
        obj = BankIdCollectResponse(response=response_factory(200, data))
        assert obj.hintCode == None
        assert obj.message == None
        assert type(obj.completionData) == BankIdCompletionData
        assert type(obj.completionData.user) == BankIdCompletionUserData
        assert type(obj.completionData.device) == BankIdCompletionDeviceData
        assert obj.completionData.user.personalNumber == '197311108711'
        assert obj.completionData.user.name == 'Jack Sparrow'
        assert obj.completionData.user.givenName == 'Jack'
        assert obj.completionData.user.surname == 'Sparrow'
        assert obj.completionData.device.ipAddress == '78.66.48.127'
        assert obj.completionData.device.uhi == 'gjLD+nM+BniMcZyTlPHVg3wu+/eW'
        assert obj.completionData.bankIdIssueDate == datetime.strptime('2024-02-12Z', '%Y-%m-%d%z')
        assert obj.completionData.signature == 'testsig'

    def test_BankIdCancelResponse(self):
        obj = BankIdCancelResponse(response=response_factory(200, {}))
        assert isinstance(obj, BankIdBaseResponse)
