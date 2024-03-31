import time
import hashlib
import hmac
import json
import re
import base64
from datetime import datetime
import urllib.parse

from requests import Response

from .listify import CollectStatuses
from .message import get_bankid_collect_message
from .exceptions import BankIdValidationError
from .message import Messages


class RequestParams():
    def __init__(self, **kwrags):
        self.kwargs = kwrags
    
    def _error(self, param, value, message):
        raise BankIdValidationError(
            f"Error: Invalid Parameter {param}: {message}.\nCurrent value: {value}"
        )
    
    def _ctype(self, param, value, ctype):
        try:
            return ctype(value)
        except:
            self._error(
                param, value, 
                f"Invalid Type. Must be instance of or can be converted to {ctype}"
            )
    
    def clean_endUserIp(self, value):
        value = self._ctype('endUserIp', value, str)

        ipv4_pattern = (
            r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        ipv6_pattern = (
            r'^([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{1,4}:){1,7}:'
            r'|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{1,4}:){1,5}'
            r'(:[0-9a-fA-F]{1,4}){1,2}$|^([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4})'
            r'{1,3}$|^([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}$|^([0-9a-fA-F]'
            r'{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}$|^[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]'
            r'{1,4}){1,6})$|:((:[0-9a-fA-F]{1,4}){1,7}|:)$'
        )

        if not re.match(ipv4_pattern, value) and not re.match(ipv6_pattern, value):
            self._error('endUserIp', value, "Must be IPV4/IPV6 ip address")
        
        return value
    
    def clean_userVisibleData(self, value):
        value = self._ctype('userVisibleData', value, str)
        
        encoded_value = base64.b64encode(value.encode('utf-8')).decode('utf-8')

        if len(encoded_value) < 1 or len(encoded_value) > 1500:
            self._error(
                'userVisibleData', len(encoded_value), 
                "Length must be between 1 to 1500 after encoding"
            )
        
        return encoded_value
    
    def clean_userNonVisibleData(self, value):
        return self.clean_userVisibleData(value)
    
    def clean_userVisibleDataFormat(self, value):
        if value is True:
            value = 'simpleMarkdownV1'
        
        if value != 'simpleMarkdownV1':
            self._error('userVisibleDataFormat', value, "Must be 'simpleMarkdownV1' or True")
        
        return value
    
    def clean_personalNumber(self, value):
        value = self._ctype('personalNumber', value, str)

        if not re.match(r'^\d{12}$', value):
            self._error('personalNumber', value, "Must be 12 digits")

        return value
    
    def clean_callInitiator(self, value):
        value = self._ctype('callInitiator', value, str)

        if value.lower() == "rp": 
            return "RP"
        if value.lower() == "user":
            return "user"
            
        self._error('callInitiator', value, "Value must be 'RP' or 'user'")
    
    def clean_requirement(self, value):
        value = self._ctype('requirement', value, dict)
        
        valid_keys = [
            'pinCode', 'mrtd', 'cardReader', 'certificatePolicies', 'personalNumber'
        ]

        [
            self._error(
                'requirement', key, f"Invalid key. valid keys: {valid_keys}"
            )
            for key in value.keys() if key not in valid_keys
        ]
        if value.get('personalNumber'):
            self.clean_personalNumber(value['personalNumber'])
        
        return value
    
    def clean_order_time(self, value):
        return self._ctype('order_time', value, int)

    def clean_orderRef(self, value):
        return self._ctype('orderRef', value, str)
    
    def clean_qrStartSecret(self, value):
        return self._ctype('qrStartSecret', value, str)
    
    def clean_qrStartToken(self, value):
        return self._ctype('qrStartToken', value, str)

    def clean(self) -> dict:
        cleaned_data = {}

        for key in self.kwargs.keys():
            value = self.kwargs[key]
            if value is None:
                continue

            if hasattr(self, f'clean_{key}'):
                cleaned_data[key] = getattr(self, f'clean_{key}')(value)
            else:
                cleaned_data[key] = value
        
        return cleaned_data


def generate_qr_data(order_time, qr_start_token, qr_start_secret):
    qr_time = str(int(time.time() - int(order_time)))
    qr_auth_code = hmac.new(qr_start_secret.encode(), qr_time.encode(), hashlib.sha256).hexdigest()
    return ".".join(["bankid", qr_start_token, qr_time, qr_auth_code])


class BankIdBaseResponse():
    def __init__(self, response: Response):
        self.response = response
        self.status_code = response.status_code
        self.data = response.json()
        self.url = response.url
    
    def __str__(self) -> str:
        return (
            f"response status: {self.status_code};\n"
            f"response data: {json.dumps(self.data)}"
        )
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__} "
            f"response status: {self.status_code};\n"
            f"response data: {json.dumps(self.data)}"
        )


class BankIdStartResponse(BankIdBaseResponse):
    def __init__(self, response, is_mobile: bool=True):
        super().__init__(response)
        
        self.orderRef = str(self.data['orderRef'])
        self.autoStartToken = str(self.data['autoStartToken'])
        self.qrStartToken = str(self.data['qrStartToken'])
        self.qrStartSecret = str(self.data['qrStartSecret'])

        self.order_time = int(time.time())
        self._is_mobile = is_mobile

    def launch_url(self, redirect='null'):
        redirect = urllib.parse.quote_plus(redirect)
        if self._is_mobile:
            return f'https://app.bankid.com/?autostarttoken={self.autoStartToken}&redirect={redirect}'
        return f"bankid:///?autostarttoken={self.autoStartToken}&redirect={redirect}"
    
    @property
    def qr_data(self):
        return generate_qr_data(self.order_time, self.qrStartToken, self.qrStartSecret)


class BankIdPhoneStartResponse(BankIdBaseResponse):
    def __init__(self, response):
        super().__init__(response)

        self.orderRef = str(self.data['orderRef'])


class BankIdCompletionUserData():
    def __init__(self, completion_data_user) -> None:
        self.personalNumber = completion_data_user.get('personalNumber')
        self.name = completion_data_user.get('name')
        self.givenName = completion_data_user.get('givenName')
        self.surname = completion_data_user.get('surname')


class BankIdCompletionDeviceData():
    def __init__(self, completion_data_device) -> None:
        self.ipAddress = completion_data_device.get('ipAddress')
        self.uhi = completion_data_device.get('uhi')


class BankIdCompletionData():
    def __init__(self, completion_data) -> None:
        self.json = completion_data

        if completion_data.get('user'):
            self.user = BankIdCompletionUserData(completion_data['user'])
        else:
            self.user = None
        
        if completion_data.get('device'):
            self.device = BankIdCompletionDeviceData(completion_data['device'])
        else:
            self.device = None
        
        if completion_data.get('bankIdIssueDate'):
            self.bankIdIssueDate = datetime.strptime(completion_data['bankIdIssueDate'], '%Y-%m-%d%z')
        else:
            self.bankIdIssueDate = None 
        self.stepUp = completion_data.get('stepUp')
        self.signature = completion_data.get('signature')
        self.ocspResponse = completion_data.get('ocspResponse')


class BankIdCollectResponse(BankIdBaseResponse):
    def __init__(self, response, qr_args=[], messages=Messages, is_mobile=True):
        super().__init__(response)

        self.orderRef = str(self.data['orderRef'])
        self.status = str(self.data['status'])
        if self.status == CollectStatuses.complete:
            self.hintCode = None
            self.message = None
            self.completionData = BankIdCompletionData(self.data['completionData'])
        else:
            self.hintCode = self.data['hintCode']
            self.message = get_bankid_collect_message(
                self.status, self.hintCode, is_mobile, messages
            )
            self.completionData = None
        
        self._qr_args = qr_args

    @property
    def qr_data(self):
        if self._qr_args and all(self._qr_args):
            return generate_qr_data(*self._qr_args)


class BankIdCancelResponse(BankIdBaseResponse):
    def __init__(self, response):
        super().__init__(response)
