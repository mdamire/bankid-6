from unittest.mock import patch
import pytest

from bankid6 import BankIdClient, BankIdValidationError, Messages, UseTypes, Languages
from bankid6.handlers import (
    BankIdStartResponse, BankIdPhoneStartResponse, BankIdCollectResponse, BankIdCancelResponse
)

from .factories import (
    TEST_START_RESPONSE, TEST_START_RESPONSE_DATA, TEST_PHONE_START_RESPONSE, TEST_PHONE_START_RESPONSE_DATA,
    TEST_COLLECT_RESPONSE, TEST_CANCEL_RESPONSE
)


def test_client():
    bc = BankIdClient(key_pem='test1')
    assert bc.api_url == "https://appapi2.test.bankid.com/rp/v6.0/"
    assert bc.key_pem == 'test1'
    assert bc.cert_pem
    assert bc.ca_pem

    with pytest.raises(KeyError):
        bc = BankIdClient(prod_env=True, key_pem='test1')
    
    bc = BankIdClient(prod_env=True, cert_pem='testc', key_pem='testk', ca_pem='testca')
    assert bc.api_url == "https://appapi2.bankid.com/rp/v6.0/"
    assert bc.key_pem == 'testk'
    assert bc.cert_pem == 'testc'
    assert bc.ca_pem == 'testca'


def test_start():
    bc = BankIdClient()

    with patch('bankid6.BankIdClient._post') as mocked:
        mocked.return_value = TEST_START_RESPONSE
        sr = bc.auth('192.168.0.1')
        assert isinstance(sr, BankIdStartResponse)
        assert bc._orderRef == TEST_START_RESPONSE_DATA['orderRef']
        assert bc._qrStartToken == TEST_START_RESPONSE_DATA['qrStartToken']
        assert bc._qrStartSecret == TEST_START_RESPONSE_DATA['qrStartSecret']
        assert bc._order_time
    
    with patch('bankid6.BankIdClient._post') as mocked:
        mocked.return_value = TEST_PHONE_START_RESPONSE
        sr = bc.phone_auth('199002113166', 'rp')
        assert isinstance(sr, BankIdPhoneStartResponse)
        assert bc._orderRef == TEST_PHONE_START_RESPONSE_DATA['orderRef']
        assert bc._qrStartToken == None
        assert bc._qrStartSecret == None
        assert bc._order_time == None
    

    with patch('bankid6.BankIdClient._post') as mocked:
        mocked.return_value = TEST_START_RESPONSE
        sr = bc.sign('192.168.0.1', userVisibleData='TEST')
        assert isinstance(sr, BankIdStartResponse)
        assert bc._orderRef == TEST_START_RESPONSE_DATA['orderRef']
        assert bc._qrStartToken == TEST_START_RESPONSE_DATA['qrStartToken']
        assert bc._qrStartSecret == TEST_START_RESPONSE_DATA['qrStartSecret']
        assert bc._order_time


    with patch('bankid6.BankIdClient._post') as mocked:
        mocked.return_value = TEST_PHONE_START_RESPONSE
        sr = bc.phone_sign('199002113166', 'user', userVisibleData='TEST',)
        assert isinstance(sr, BankIdPhoneStartResponse)
        assert bc._orderRef == TEST_PHONE_START_RESPONSE_DATA['orderRef']
        assert bc._qrStartToken == None
        assert bc._qrStartSecret == None
        assert bc._order_time == None


def test_collect():
    bc = BankIdClient()

    with patch('bankid6.BankIdClient._post') as mocked:
        mocked.return_value = TEST_START_RESPONSE
        bc.auth('192.168.0.1')
    
    with patch('bankid6.BankIdClient._post') as mocked:
        mocked.return_value = TEST_COLLECT_RESPONSE
        cr = bc.collect()
        assert isinstance(cr, BankIdCollectResponse)
    
    with pytest.raises(BankIdValidationError):
        BankIdClient().collect()


def test_collect_message():
    class MyMessage(Messages):
        RFA1 = {'test': 'yes'}
        RFA13 = ('swetext', 'entext')

    bc = BankIdClient(messages=MyMessage)
    
    with patch('bankid6.BankIdClient._post') as mocked:
        mocked.return_value = TEST_START_RESPONSE
        bc.auth('192.168.0.1')
    
    with patch('bankid6.BankIdClient._post') as mocked:
        mocked.return_value = TEST_COLLECT_RESPONSE
        cr = bc.collect()
        assert cr.message[UseTypes.qrcode] == {'test': 'yes'}
        assert cr.message[UseTypes.onfile][Languages.en] == 'entext'
        assert cr.message[UseTypes.onfile][Languages.sv] == 'swetext'


def test_cancel():
    bc = BankIdClient()

    with patch('bankid6.BankIdClient._post') as mocked:
        mocked.return_value = TEST_START_RESPONSE
        bc.auth('192.168.0.1')

    with patch('bankid6.BankIdClient._post') as mocked:
        mocked.return_value = TEST_CANCEL_RESPONSE
        cr = bc.cancel()
        assert isinstance(cr, BankIdCancelResponse)
    
    with pytest.raises(BankIdValidationError):
        BankIdClient().collect()

