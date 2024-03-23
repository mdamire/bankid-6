import time
import hashlib
import hmac


class StartParams():
    def __init__(self, **kwrags):
        self.kwargs = kwrags
    
    def clean_endUserIp(self, value):
        return True
    
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


class BankIdStartResponse():
    def __init__(self, response, is_mobile: bool=True):
        response_data = response.json()
        
        self.orderRef = str(response_data['orderRef'])
        self.autoStartToken = str(response_data['autoStartToken'])
        self.qrStartToken = str(response_data['qrStartToken'])
        self.qrStartSecret = str(response_data['qrStartSecret'])

        self.order_time = time.time()

        self.response = response
        self.is_mobile = is_mobile

    def launch_url(self, redirect='null'):
        if self.is_mobile:
            return f'https://app.bankid.com/?autostarttoken={self.autoStartToken}&redirect={redirect}'
        return f"bankid:///?autostarttoken={self.autoStartToken}&redirect={redirect}"
    
    @property
    def qr_data(self):
        return _qr_data(self.order_time, self.qrStartToken, self.qrStartSecret)

