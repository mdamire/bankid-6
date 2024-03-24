import time
import hashlib
import hmac
import json
from requests import Response

from .listify import CollectStatuses
from .message import get_bankid_collect_message


class RequestParams():
    def __init__(self, **kwrags):
        self.kwargs = kwrags
    
    def clean_endUserIp(self, value):
        return value
    
    def clean_userVisibleDataFormat(self, value):
        if value is True:
            value = 'simpleMarkdownV1'
        
        return value

    def clean(self):
        cleaned_data = {}

        for key in self.kwargs.keys():
            value = self.kwargs[key]
            if value is None:
                continue

            if hasattr(self, f'clean_{key}'):
                cleaned_data[key] = str(getattr(self, f'clean_{key}')(value))
            else:
                cleaned_data[key] = str(value)
        
        return cleaned_data


def _qr_data(order_time, qr_start_token, qr_start_secret):
    qr_time = str(int(time.time() - int(order_time)))
    qr_auth_code = hmac.new(qr_start_secret.encode(), qr_time.encode(), hashlib.sha256).hexdigest()
    return ".".join(["bankid", qr_start_token, qr_time, qr_auth_code])


class BankIdBaseResponse():
    def __init__(self, response: Response):
        self.response = response
        self.response_status = response.status_code
        self.response_data = response.json()
        self.url = response.url
    
    def __str__(self) -> str:
        return (
            f"response status: {self.response_status};\n"
            f"response data: {json.dumps(self.response_data)}"
        )
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__} "
            f"response status: {self.response_status};\n"
            f"response data: {json.dumps(self.response_data)}"
        )


class BankIdStartResponse(BankIdBaseResponse):
    def __init__(self, response, is_mobile: bool=True):
        super().__init__(response)
        
        self.orderRef = str(self.response_data['orderRef'])
        self.autoStartToken = str(self.response_data['autoStartToken'])
        self.qrStartToken = str(self.response_data['qrStartToken'])
        self.qrStartSecret = str(self.response_data['qrStartSecret'])

        self.order_time = int(time.time())
        self.is_mobile = is_mobile

    def launch_url(self, redirect='null'):
        if self.is_mobile:
            return f'https://app.bankid.com/?autostarttoken={self.autoStartToken}&redirect={redirect}'
        return f"bankid:///?autostarttoken={self.autoStartToken}&redirect={redirect}"
    
    @property
    def qr_data(self):
        return _qr_data(self.order_time, self.qrStartToken, self.qrStartSecret)


class BankIdPhoneStartResponse(BankIdBaseResponse):
    def __init__(self, response):
        super().__init__(response)

        self.orderRef = str(self.response_data['orderRef'])


class BankIdCompletionUserData():
    def __init__(self, completion_data_user) -> None:
        self.personalNumber = completion_data_user['personalNumber']
        self.name = completion_data_user['name']
        self.givenName = completion_data_user['givenName']
        self.surname = completion_data_user['surname']


class BankIdCompletionDeviceData():
    def __init__(self, completion_data_device) -> None:
        self.ipAddress = completion_data_device['ipAddress']
        self.uhi = completion_data_device['uhi']


class BankIdCompletionData():
    def __init__(self, completion_data) -> None:
        self.json = completion_data

        self.user = BankIdCompletionUserData(completion_data['user'])
        self.device = BankIdCompletionUserData(completion_data['device'])
        # TODO: make it to date object
        self.bankIdIssueDate = completion_data['bankIdIssueDate']
        self.stepUp = completion_data['stepUp']
        self.signature = completion_data['signature']
        self.ocspResponse = completion_data['ocspResponse']


class BankIdCollectResponse(BankIdBaseResponse):
    def __init__(self, response, qr_args, messages, is_mobile):
        super().__init__(response)

        self.orderRef = str(self.response_data['orderRef'])
        self.status = str(self.response_data['status'])
        if self.status == CollectStatuses.complete:
            self.hintCode = None
            self.message = None
            self.completionData = BankIdCompletionData(self.response_data['completionData'])
        else:
            self.hintCode = self.response_data['hintCode']
            self.message = get_bankid_collect_message(
                self.status, self.hintCode, is_mobile, messages
            )
            self.completionData = None
        
        self.qr_args = qr_args

    @property
    def qr_data(self):
        if not all(self.qr_args):
            return
        return _qr_data(*self.qr_args)


class BankIdCancelResponse(BankIdBaseResponse):
    def __init__(self, response):
        super().__init__(response)
