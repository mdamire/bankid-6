# bankid6

<br/>

## Overview

A complete implementation of Swedish BankID authentication system version 6.  It includes initiating/collecting/canceling authentication orders, user Messages and exception handling according to [BankID Documentaion](https://www.bankid.com/en/utvecklare/guider/teknisk-integrationsguide/rp-introduktion).
<br/>
<br/>

## Installation

```
pip install bankid6
```
Supports python version 3.6 and later.

<br/>
<br/>

## Quick Start

The following sample script can get you started quickly. There are more functionalities and customization options than what has been shown here.


```python
import time
from bankid6 import BankIdClient, CollectStatuses, UseTypes, Languages, BankIdError, HintCodes


# Instantiate client. is_mobile means if it's starting from mobile device
# For production environment use parameters: 
# prod_env=True, cert_pem=<certificate_filepath>, key_pem='<key_filepath>', ca_pem='<ca_filepath>'
bankid_client = BankIdClient(is_mobile=False)

try:

    # Start the authentication order. other methods are sign, phone_auth, phone_sign
    # Takes parameters according to BankID documentation
    start_response = bankid_client.auth('192.168.0.1')

except BankIdError as bie:

    if bie.message:
        # If the message is available then it's sufficient just to show the message to the user.
        # No more action is needed. 
        print("User Message: ", bie.message[Languages.en])
    
    else:
        # reason and action are from bankid documentaion. 
        # also, response_data, response_status attributes are available
        raise Exception(f"Fatal error. reason: {bie.reason}; action needed: {bie.action}; response data: {bie.response_data}; response status: {bie.response_status}") from bie

# qr_data gives the calculated data to make qr code. 
# subsequent values can be found from collect method
print('QR data: ', start_response.qr_data)

# launch url give you the full url which you need to launch BankID app on current device.
# It changes depending on is_mobile parameter of client
# redirect="null" by default
print('Launch url: ', start_response.launch_url(redirect="https://www.google.com"))


while True:
    time.sleep(1)

    try:

        # Collect the status of order which was initiated with auth/sign/phone_auth/phone_sign method

        # It takes optional parameter which is useful if you want to call collect from different client that you use to initiate the order
        # Optional prameters: orderRef, qrStartToken, qrStartSecret, order_time
        # These values are available as start_response attributes. e.g start_response.orderRef
        collect_response = bankid_client.collect()
    
    except BankIdError as bie:

        if bie.message:
            # Same as before
            print(bie.message[Languages.en])
            break
        
        else:
            # same as before
            raise Exception(f"Fatal error. reason: {bie.reason}; action needed: {bie.action}; response data: {bie.response_data}; response status: {bie.response_status}") from bie


    # CollectStatuses can be used to easily check statuses. No need to copy form documentation. No room for error.
    if collect_response.status == CollectStatuses.complete:

        # completionData contains all the nested parsed value in python's datatype
        # the structure is exactly as documentation. e.g collect_response.completionData.user.personalNumber
        print('Authenticated by: ', collect_response.completionData.user.name)
        break

    else:

        # Easily check HintCodes against HintCodes class attributes
        if collect_response.hintCode == HintCodes.outstandingTransaction:

            # collect response also provides calculated QR data to make QR code
            # If collect method is called from different client instance than where the was initiated
            # then qrStartToken, qrStartSecret, order_time parameters are needed to supply to collect method to get Calculated QR data
            print('QR data: ', collect_response.qr_data)
        
        # collect response has appropriate messages according to BankID. The message is a dict object.
        # UseTypes class has attributes describing if the authentication is started via QR code or Auto Staring app on current device
        # Language class has 'en' and 'sv' attributes
        print("User Message: ", collect_response.message[UseTypes.qrcode][Languages.en])
        
        # failed response also has message which is printed above
        if collect_response.status == CollectStatuses.failed:
            break

```

<br/>
<br/>

## User Guide

### 1. Instantiate `BankIdClient` Class

`BankIdClient` provides functionality to initiate authentication or signing orders, collect order results or cancel the order.

Instantiate for `BankIdClient` for test environment.
```
>>> from bankid6 import BankIdClient
>>> bankid_client = BankIdClient()
```
This instance will use BankID test url, test certificates which are provided in the package. It's configured for computers. It can be initialized for mobile devices which helps to render correct messages and correct urls for launching the app.
```
>>> bankid_client = BankIdClient(is_mobile=True)            # Default to False
```
<br/>

To initialize for a production environment, ensure that the `prod_env` parameter is set to `True`. Additionally, you must provide the file paths for the certificate, the private key associated with the certificate, and the CA certificate.
```
>>> bankid_client = BankIdClient(prod_env=True, cert_pem=<certificate_filepath>, key_pem='<private_key_filepath>', ca_pem=<ca_certificate_filepath>)
```
<br/>
<br/>

### 2. Initiate Authentication or Signing Order

The `BankIdClient` offers `auth` and `sign` methods to initiate authentication and signing orders, respectively. These methods return a `BankIdStartResponse` object, which contains attributes to easily get the data for QR code and url for launching the BankID app.

```
>>> bankid_client = BankIdClient()
>>> start_response = bankid_client.auth('192.168.0.1')      # Takes IP of end user

>>> start_response.qr_data                                  # Calculated data to create QR code
'bankid.c03da000-d5de-4435-b81b-66154960784d.8.7a7f4a36307cb8d8ddb4fe86116764819def4c32c55d1ba792e6e4117be9a5a1'

>>> start_response.launch_url()                             # Depends on is_mobile parameter of the BankIdClient
'bankid:///?autostarttoken=aaba5bef-1066-42da-b6c6-0730b8c53997&redirect=null'

>>> start_response.launch_url('https://www.google.com')     # Takes a redirect url as parameter
'bankid:///?autostarttoken=aaba5bef-1066-42da-b6c6-0730b8c53997&redirect=https%3A%2F%2Fwww.google.com'

>>> [attr for attr in dir(start_response) if not attr.startswith('_')]
['autoStartToken', 'data', 'launch_url', 'orderRef', 'order_time', 'qrStartSecret', 'qrStartToken', 'qr_data', 'response', 'status_code', 'url']
```

Subsequent QR data can be found in response of the `collect` method or from the `generate_qr_data` function.
```
>>> from bankid6 import generate_qr_data
>>> generate_qr_data(start_response.order_time, start_response.qrStartToken, start_response.qrStartSecret)
'bankid.c03da000-d5de-4435-b81b-66154960784d.250.16f0f42bb4f1a99d41a31e38cd54866fce5a193e277f4d48339a7579ac51fe4e'
```
<br>

The `BankIdClient` also has `phone_auth` and `phone_sign` methods that initiate authentication and signing orders while the customer is on the phone. You need to pass a personal number and the BankID will send the request to the customer's BankID app. These methods return a `BankIdPhoneStartResponse` object.
```
>>> phone_start_response = BankIdClient().phone_auth('199002113166', callInitiator="RP")
>>> [attr for attr in dir(phone_start_response) if not attr.startswith('_')]
['data', 'orderRef', 'response', 'status_code', 'url']
```

Both `sign` and `phone_sign` methods require the `userVisibleData` parameter.
```
>>> BankIdClient().sign('192.168.0.1', userVisibleData="Hello! Sign this test documents")
<class 'bankid6.handlers.BankIdStartResponse'> response status: 200;
response data: {"orderRef": "6eaf4368-22ae-4309-8768-f58b772d1617", "autoStartToken": "3d973332-8abe-4273-b292-b16c975a1a39", "qrStartToken": "29d0b198-487d-42b8-91a8-c63fc94a2733", "qrStartSecret": "a611ccd5-5940-4160-9fde-20a251716bfb"}
```

These methods have required or optional parameters exactly as described in BankID documentation. These parameters are validated, processed as BankID requires and sent as the data of the request to the BankID.

The returned objects are derived from `BankIdBaseResponse`, parses any BankID response, creating an attribute with the same name as the key of the response data. `BankIdBaseResponse` has attributes related to actual HTTP response. This is also True for `collect` or `cancel`.

See the API Reference section for comprehensive documentation detailing parameters and return values.
<br/>
<br/>

### 3. Collect Order Result

Use `collect` method of `BankIdClient` object to get the order result.
```
>>> from bankid6 import BankIdClient
>>> bankid_client = BankIdClient()

>>> bankid_client.auth('192.168.0.1')
<class 'bankid6.handlers.BankIdStartResponse'> response status: 200
response data: {"orderRef": "ccc9b028-4c83-49f8-b5ae-a3bac54a7427", "autoStartToken": "96c45dea-d14c-4bc5-bf30-db4015d39da9", "qrStartToken": "d550a68e-1e4d-4d66-8dce-3c6497c8da73", "qrStartSecret": "4b3bba21-ebaa-4bf4-8856-e66271550b78"}

>>> bankid_client.collect()
<class 'bankid6.handlers.BankIdCollectResponse'> response status: 200;
response data: {"orderRef": "ccc9b028-4c83-49f8-b5ae-a3bac54a7427", "status": "pending", "hintCode": "outstandingTransaction"}
```

It returns `BankIdCollectResponse` which is derived from `BankIdBaseResponse` class.
```
>>> collect_response = bankid_client.collect()
>>> collect_response.status                             # BankID status from response data
'pending'
>>> collect_response.qr_data                            # calculates qr data according to the time             
'bankid.d9c9339c-b9d3-48a2-8289-8d66e1d28a08.21.941023af5b86d5b16aaa226ad7130ee08a1dcdca89e199639a3986336a0569fb'
>>> from bankid6 import CollectStatuses
>>> collect_response.status == CollectStatuses.pending  # don't have to remember status values
True
```

Like the BankID documentation, the response object provides information in `completionData` (object of `BankIdCompletionData`) attribute when status is "complete".

```
>>> cr = bankid_client.collect()
>>> print(cr.completionData.user.personalNumber) if cr.status == CollectStatuses.complete else print(cr.hintCode)
```

It's possible to decouple the collect method from order initiating methods.

```
>>> sr = BankIdClient().auth('192.168.0.1')
>>> cr = BankIdClient().collect(orderRef=sr.orderRef, qrStartToken=sr.qrStartToken, qrStartSecret=sr.qrStartSecret, order_time=sr.order_time)
>>> cr.qr_data
'bankid.d9c9339c-b9d3-48a2-8289-8d66e1d28a08.21.941023af5b86d5b16aaa226ad7130ee08a1dcdca89e199639a3986336a0569fb'
```
The `orderRef` parameter is used to find the order and `qrStartToken`, `qrStartSecret` and `order_time` parameters are used to calculate the QR code. The `qr_data` attribute in the `BankIdCollectResponse` object is accessible if the `collect` method is invoked from the same client where order was initiated, or if these parameters are provided.

#### User Message

`BankIdCollectResponse` also has a `message` attribute which contains user messages according to BankID documentation when the status is 'pending' or 'failed'. A message depends on how order was initiated and the language. Each message is a dict constructed like this:
```python
{
    "qrcode": {             # order initiated by scanning qr code
        "swedish": "",
        "english": ""
    },
    "onfile": {             # order initiated by starting the bankid app on the same device
        "swedish": "",
        "english": ""
    }
} 
```

`UseTypes` and `Languages` classes can be used to extract the correct message easily.

```
>>> cr = bankid_client.collect()
>>> from bankid6 import UseTypes, Languages
>>> print(cr.message[UseTypes.qrcode][Languages.en]) if cr.status in [CollectStatuses.complete, CollectStatuses.failed]
'Start your BankID app.'
```

You can make a subclass of `Messages`, override its existing messages and pass it to`BankIdClient` as a parameter. Any message in `Messages` class is an attribute which starts with 'RFA' as in BankID documentation.
```python
from bankid6 import Messages

print(Messages.RFA1.help_text) # prints 'status=pending, hintCode=outstandingTransaction, hintCode=noClient'

class MyMessage(Messages):
    RFA1 = {'test': 'yes'}
    RFA13 = ('<h3>swedish message<h3>', '<h3>english message</h3>')

bankid_client = BankIdClient(messages=MyMessage)
```
Their value can be a dict or a tuple of swedish and english messages. If the value is dict, it is returned as it is from `message` attribute of `BankIdCollectResponse` object.
<br/>
<br/>

### 4. Cancel Order
Use `cancel` mothod of `BankIdClient` object to cancel the order.
```
>>> bankid_client = BankIdClient()

>>> bankid_client.auth('192.168.0.1')
<class 'bankid6.handlers.BankIdStartResponse'> response status: 200
response data: {"orderRef": "ccc9b028-4c83-49f8-b5ae-a3bac54a7427", "autoStartToken": "96c45dea-d14c-4bc5-bf30-db4015d39da9", "qrStartToken": "d550a68e-1e4d-4d66-8dce-3c6497c8da73", "qrStartSecret": "4b3bba21-ebaa-4bf4-8856-e66271550b78"}

>>> bankid_client.cancel()
<class 'bankid6.handlers.BankIdCancelResponse'> response status: 200;
response data: {}
```

This can be decoupled by using its `orderRef` parameter.

```
>>> start_response = BankIdClient().auth('192.168.0.1')
>>> BankIdClient().auth(orderRef=start_response.orderRef)
<class 'bankid6.handlers.BankIdCancelResponse'> response status: 200;
response data: {}
```
<br/>
<br/>

### 5. Exceptions

All methods in `BankIdClient` can raise `BankIdError` or `BankIdValidationError`. 

`BankIdError` is raised when a request is made to BankID server and it returns an error. It has `message` attribute with structure like:
```json
{
    "swedish": "",
    "english": ""
}
```
If the message is available, it indicates that the message should be presented to the customer without any additional action required. Otherwise, the `reason` and `action` attributes can provide information on why the error occurred and what steps need to be taken to address it according to BankID documentation. Attribute `response_data` has the data received from BankID in dict format. See Api Reference section for more functionalities.


`BankIdValidationError` is raised before sending the request to BankID if any parameter is invalid.

<br/>
<br/>
<br/>
<br/>

## API Reference


#### class BankIdClient()

**def __init__(self, prod_env: bool=False, cert_pem: str=None, key_pem: str=None, ca_pem: str=None, request_timeout: int=None, messages: Messages=Messages, is_mobile: bool=False)**

**Parameters:**
- `prod_env` indicates if it's a production environment. Test or prod urls are chosen based on this. If it is `True` then `key_pem`, `cert_pem` and `ca_pem` are required. Otherwise test certificates which are already included in the package will be used. Any or all of the certificates can also be provided when the value is `False`
- `cert_pem` file path of the certificate file
- `key_pem` file path of the private key of the certificate.
- `ca_pem` file path of CA certificate file
- `request_timeout` number of seconds to wait for response
- `messages` class or subclass of `Messages` class to override existing message
- `is_mobile` if it's being used in a mobile device.
<br/>
<br/>

**def auth(endUserIp: str, requirement: dict=None, userVisibleData: str=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None):**

Starts the BankID auth process. Use this when only user authentication is needed.

**Parameters:**
- `endUserIp` ***Required***. *str*. The user IP address as seen by RP. IPv4 and IPv6 are allowed.
- `requirement` *Optional*. *dict | object that can be converted to dict*. Requirements dictionary on how the auth order must be performed. See BankID documentation for more details. 
- `userVisibleData` *Optional*. *str*. Text displayed to the user during authentication with BankID. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `userNonVisibleData` *Optional*. *str*. Text that is not displayed to the user. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `userVisibleDataFormat` *Optional*. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

**Return:** `BankIdStartResponse`
<br/>
<br/>

**def sign(endUserIp: str, userVisibleData: str, requirement: dict=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None)**

Starts the BankID sign process. Use this when user is authenticated to sign something.

**Parameters:**
- `endUserIp` ***Required***. *str*. The user IP address as seen by RP. IPv4 and IPv6 are allowed.
- `userVisibleData` ***Required***. *str*. Text displayed to the user during authentication with BankID. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `requirement` *Optional*. *dict | object that can be converted to dict*. Requirements dictionary on how the auth order must be performed. See BankID documentation for more details. 
- `userNonVisibleData` *Optional*. *str*. Text that is not displayed to the user. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `userVisibleDataFormat` *Optional*. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

**Return:** `BankIdStartResponse`
<br/>
<br/>

**def phone_auth(personalNumber: str, callInitiator: str, requirement: dict=None, userVisibleData: str=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None)**

Initiates an authentication order when the user is talking to the RP over the phone. 

**Parameters:**
- `personalNumber` ***Required***. *str*. Any valid 12 digit personal number of the user.
- `callInitiator` ***Required***. *str*. choice between 'user' or 'RP'.
- `requirement` *Optional*. *dict | object that can be converted to dict*. Requirements dictionary on how the auth order must be performed. See BankID documentation for more details. 
- `userVisibleData` *Optional*. *str*. Text displayed to the user during authentication with BankID. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `userNonVisibleData` *Optional*. *str*. Text that is not displayed to the user. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `userVisibleDataFormat` *Optional*. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

**Return:** `BankIdPhoneStartResponse`
<br/>
<br/>

**def phone_sign(personalNumber, callInitiator, userVisibleData, requirement=None, userNonVisibleData=None, userVisibleDataFormat=None)**

Initiates an signing order when the user is talking to the RP over the phone.

**Parameters:**
- `personalNumber` ***Required***. *str*. Any valid 12 digit personal number of the user.
- `callInitiator` ***Required***. *str*. choice between 'user' or 'RP'.
- `userVisibleData` ***Required***. *str*. Text displayed to the user during authentication with BankID. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `requirement` *Optional*. *dict | object that can be converted to dict*. Requirements dictionary on how the auth order must be performed. See BankID documentation for more details. 
- `userNonVisibleData` *Optional*. *str*. Text that is not displayed to the user. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `userVisibleDataFormat` *Optional*. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

**Return:** `BankIdPhoneStartResponse`
<br/>
<br/>

**def collect(orderRef: str=None, qrStartToken: str=None, qrStartSecret: str=None, order_time: int=None)**

Collect the result of the `auth`, `sign`, `phone_auth` or `phone_sign` methods. If used from same client instance when order was initiated, it doesn't require any parameters

- `orderRef` *Optional*. *str*. Can be found in response object from any order initiator methods. If given then the corresponding order result will be requested. Useful when the method is being used from the different client instance than where the order was started.
- `qrStartToken` *Optional*. *str*. Can be found in response object from any order initiator methods. If given, it will be used to calculate QR data.
- `qrStartSecret` *Optional*. *str*. Can be found in response object from any order initiator methods. If given, it will be used to calculate QR data.
- `order_time` *Optional*. *int*. Can be found in response object from any order initiator methods. If given, it will be used to calculate QR data.

**Return:** `BankIdCollectResponse`
<br/>
<br/>

**def cancel(orderRef: str=None):**

Cancels an ongoing sign or auth order. If used from same client instance when order was initiated, it doesn't require any parameters

- `orderRef` *Optional*. *str*. Can be found in response object from any order initiator methods. If given then the corresponding order result will be requested. Useful when the method is being used from the different client instance than where the order was started.

**Return:** `BankIdCancelResponse`

<br/>
<br/>
<br/>

### class BankIdBaseResponse()

`response`: *requests.Response*. object which was returned from sending the request.
`status`: *int*. Http response code of the response
`data`: *dict*. returned data in dict format
`url`: *str*. The full url where the request was sent

<br/>
<br/>
<br/>

### class BankIdStartResponse(BankIdBaseResponse):

`orderRef`: *str*. Used to collect the status of the order. Parsed from BankID response.
`autoStartToken`: *str*. Used to compile the start url. Parsed from BankID response.
`qrStartToken`: *str*. Used to compute the animated QR code. Parsed from BankID response.
`qrStartSecret`: *str*. Used to compute the animated QR code. Parsed from BankID response.
`order_time`: *int*. order time in seconds since the Epoch.

<br/>
<br/>
<br/>

### class BankIdPhoneStartResponse(BankIdBaseResponse):

`orderRef`: *str*. Used to collect the status of the order. Parsed from BankID response.

<br/>
<br/>
<br/>

### class BankIdCollectResponse(BankIdBaseResponse)

`orderRef`: *str*. Used to collect the status of the order. Parsed from BankID response.
`status`: *str*. 'pending' | 'complete' | 'failed'. Parsed from BankID response.
`hintCode`: *str*. Only present for pending and failed orders. Parsed from BankID response.
`completionData`: *BankIdCompletionData*. Only present for complete orders. Parsed from BankID response.
`message`: *dic*. User message according to bankid documentation. which has following format:
```python
{
    "qrcode": {             # order initiated by scanning qr code
        "swedish": "",
        "english": ""
    },
    "onfile": {             # order initiated by starting the bankid app on the same device
        "swedish": "",
        "english": ""
    }
} 
```
<br/>
<br/>

### class BankIdCompletionData()
`user`: *BankIdCompletionUserData*. Authenticated user information.
`device`: *BankIdCompletionDeviceData*. Authenticated user's device information.
`bankIdIssueDate`: *datetime*. The date the BankID was issued to the user.
`stepUp`: *str*. Information about extra verifications that were part of the transaction.
`signature`: *str*. The signature as described in the BankID Signature Profile specification. Base64-encoded.
`ocspResponse`: *str*. The OCSP response. Base64-encoded. The OCSP response is signed by a certificate that has the same issuer as the certificate being verified. The OSCP response has an extension for Nonce. The nonce is calculated as:
- SHA-1 hash over the base 64 XML signature encoded as UTF-8.
- 12 random bytes are added after the hash.
- The nonce is 32 bytes (20 + 12).
`json`: *dict*. Completion data in dict format.
<br/>

### class BankIdCompletionUserData()
`personalNumber`: *str*. The personal identity number.
`name`: *str*. The given name and surname of the user.
`givenName`: *str*. The given name of the user.
`surname`: *str*. The surname of the user.
<br/>
<br/>

### class BankIdCompletionDeviceData()
`ipAddress`: *str*. The IP address of the user agent as the BankID server discovers it. When an order is started with autoStartToken the RP can check that this matchs the IP they observe to ensure session fixation String.
`uhi`: *str*. Unique hardware identifier for the user's device.

<br/>
<br/>
<br/>

### class BankIdCancelResponse(BankIdBaseResponse)
***...***

<br/>
<br/>
<br/>

### class BankIdError(Exception)
`reason`: *str*. Reason of the exception according to the BankID Documentation
`action`: *str*. What action is needed for this exception according to BankID Documentation
`message`: *dict*. Message for users.
`errorCode`: *str*. Error code received in response data
`response`: *requests.Response*. object which was returned from sending the request.
`response_status`: *int*. Http response code of the response
`response_data`: *dict*. returned data in dict format

<br/>
<br/>
<br/>

### class BankIdValidationError(Exception)
***...***

<br/>
<br/>
<br/>


***Any comments or reports on the Github [issue page]("https://github.com/mdamire/bankid-6/issues") are much appreciated.***
