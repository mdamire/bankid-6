# bankid-6

### Instantiate `BankIdClient` Class

`BankIdClient` provides functionality to initiate authentication or signing order, collect order result or cancel the order.

Instantiate for `BankIdClient` for test environment.
```
>>> bankid_client = BankIdClient()
```
This instance will use BankID test url, test certificates which are provided in the package. It's configured for computers.
It can be initialized for mobile devices which helps to render correct message and correct url for launching the app.
```
>>> bankid_client = BankIdClient(is_mobile=True)            # Default to False
```

To initialize for a production environment, ensure that the `prod_env` parameter is set to `True`. Additionally, you must provide the file paths for the certificate, the private key associated with the certificate, and the CA certificate.
```
>>> bankid_client = BankIdClient(prod_env=True, cert_pem=<certificate_filepath>, key_pem='<private_key_filepath>', ca_pem=<ca_certificate_filepath>)
```
<br/>

### Initiate Authentication or Signing Order

The `BankIdClient` offers `auth` and `sign` methods to initiate authentication and signing orders, respectively, either through a QR code or the BankID app on the same device. These methods return a `BankIdStartResponse` object, which contains attributes to easily get the data for QR code and url for launching the BankID app.

```
>>> bankid_client = BankIdClient()
>>> start_response = bankid_client.auth('192.168.0.1')      # Takes IP of end user
>>> start_response.qr_data                                  # Calculated from BankID response
>>> start_response.launch_url()                             # Depends on is_mobile parameter of the BankIdClient
>>> start_response.launch_url('https://www.google.com')     # Takes a redirect url as parameter
>>> dir(start_response)
```

The `BankIdClient` also has `phone_auth` and `phone_sign` methods initiate authentication and signing orders while the customer is on the phone. You need to pass a personal number and the BankID will send the request to the customer's BankID app. These methods return a `BankIdPhoneStartResponse` object.
```
>>> bankid_client = BankIdClient()
>>> phone_start_response = bankid_client.phone_auth('199002113166', callInitiator="RP")
>>> dir(phone_start_response)
```

Both `sign` and `phone_sign` methods require `userVisibleData` parameter.
```
>>> bankid_client = BankIdClient()
>>> bankid_client.sign('192.168.0.1', userVisibleData="Hello! Sign this test documents")
```

These methods have required or optional parameters exactly as described in BankID documentation. These parameters are validated, processed as BankID requires and sent as the data of the request to the BankID.

The returned objects are derived from `BankIdBaseResponse`, parses any BankID response, creating an attribute with the same name as the key of the response data. `BankIdBaseResponse` has attributes related to HTTP response. This is also True for `collect` or `cancel`.

See the API Reference section for comprehensive documentation detailing parameters and return values.
<br/>

### Collect Order Result

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
>>> collect_response.status                             # gives the value of the status
>>> collect_response.qr_data                            # calculates qr data according to the time             
>>> from bankid6 import `CollectStatuses`
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
>>> BankIdClient().collect(orderRef=sr.orderRef, qrStartToken=sr.qrStartToken, qrStartSecret=sr.qrStartSecret, order_time=sr.order_time)
```
`orderRef` parameter is used to find the order and `qrStartToken`, `qrStartSecret` and `order_time` parameters are used to calculate the QR code. QR data is accessible in the response of `collect` if the method is invoked from the same client where order was initiated, or if these parameters are provided.

`BankIdCollectResponse` also has `message` attribute which contains user message according to BankID documentation when the status is 'pending' or 'failed'. A message depends on how order was initiated and the language. Each message is a dict constructed like this:
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
```
<br/>

### Cancel Order
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

This can be decouple by using it's `orderRef` parameter.

```
>>> start_response = BankIdClient().auth('192.168.0.1')
>>> BankIdClient().auth(orderRef=start_response.orderRef)
<class 'bankid6.handlers.BankIdCancelResponse'> response status: 200;
response data: {}
```
<br/>

### Exceptions

All methods in `BankIdClient` can raise `BankIdError` or `BankIdValidationError`. 

`BankIdError` is raised when a request is made to BankID server and it returned an error. It has `message` attribute with structure like:
```json
{
    "swedish": "",
    "english": ""
}
```
If the message is available, it indicates that the message should be presented to the customer without any additional action required. In cases where the message is unavailable, the `reason` and `action` attributes can provide information on why the error occurred and what steps need to be taken to address it.


`BankIdValidationError` is raised before sending the request to BankID if any parameter is invalid.

<br/>
<br/>

## Sample Script
---

```python
import time
from bankid6 import BankIdClient, CollectStatuses, UseTypes, Languages, BankIdError

bankid_client = BankIdClient()

try:
    start_response = bankid_client.auth('192.168.0.1')
except BankIdError as bie:
    if bie.message:
        print(bie.message[Languages.en])
    else:
        raise Exception(f"Fatal error. reason: {bie.reason}; action needed: {bie.action}") from bie

print('QR data: ', start_response.qr_data)
print('Launch url: ', start_response.launch_url())


while True:
    time.sleep(1)

    try:
        collect_response = bankid_client.collect()
    except BankIdError as bie:
        if bie.message:
            print(bie.message[Languages.en])
            break
        else:
            raise Exception(f"Fatal error. reason: {bie.reason}; action needed: {bie.action}") from bie

    if collect_response.status == CollectStatuses.complete:
        print('Authenticated by: ', collect_response.completionData.user.name)
        break
    else:
        if collect_response.hintCode == 'outstandingTransaction':
            print('QR data: ', collect_response.qr_data)
        
        print(collect_response.message[UseTypes.qrcode][Languages.en])
        
        if collect_response.status == CollectStatuses.failed:
            break
```

<br/>
<br/>

## API Reference
---


#### class BankIdClient()
<br/>

##### def __init__(self, prod_env: bool=False, cert_pem: str=None, key_pem: str=None, ca_pem: str=None, request_timeout: int=None, messages: Messages=Messages, is_mobile: bool=False)

**Parameters:**
- `prod_env` indicates if it's a production environment. Test or prod urls are chosen based on this. If it is `True` then `key_pem`, `cert_pem` and `ca_pem` are required. Otherwise test certificates which are already included in the package will be used. Any or all of the certificates can also be provided when the value is `False`
- `cert_pem` file path of the certificate file
- `key_pem` file path of the private key of the certificate.
- `ca_pem` file path of CA certificate file
- `request_timeout` number of seconds to wait for response
- `messages` class or subclass of `Messages` class to override existing message
- `is_mobile` if it's being used in a mobile device.
<br/>

##### def auth(endUserIp: str, requirement: dict=None, userVisibleData: str=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None):

Starts the bankid auth process. Use this when only user authentication is needed.

**Parameters:**
- `endUserIp` ***Required***. *str*. The user IP address as seen by RP. IPv4 and IPv6 is allowed.
- `requirement` *Optional*. *dict | object that can be converted to dict*. Requirements dictionary on how the auth order must be performed. See BankID documentation for more details. 
- `userVisibleData` *Optional*. *str*. Text displayed to the user during authentication with BankID. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `userNonVisibleData` *Optional*. *str*. Text that is not displayed to the user. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `userVisibleDataFormat` *Optional*. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

**Return:** `BankIdStartResponse`
<br/>

##### def sign(endUserIp: str, userVisibleData: str, requirement: dict=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None)

Starts the bankid sign process. Use this when user is authenticated to sign something.

**Parameters:**
- `endUserIp` ***Required***. *str*. The user IP address as seen by RP. IPv4 and IPv6 is allowed.
- `userVisibleData` ***Required***. *str*. Text displayed to the user during authentication with BankID. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `requirement` *Optional*. *dict | object that can be converted to dict*. Requirements dictionary on how the auth order must be performed. See BankID documentation for more details. 
- `userNonVisibleData` *Optional*. *str*. Text that is not displayed to the user. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
- `userVisibleDataFormat` *Optional*. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

**Return:** `BankIdStartResponse`
<br/>

##### def phone_auth(personalNumber: str, callInitiator: str, requirement: dict=None, userVisibleData: str=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None)

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

##### def phone_sign(personalNumber, callInitiator, userVisibleData, requirement=None, userNonVisibleData=None, userVisibleDataFormat=None)

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

##### def collect(orderRef: str=None, qrStartToken: str=None, qrStartSecret: str=None, order_time: int=None)

Collect the result of the `auth`, `sign`, `phone_auth` or `phone_sign` methods. If used from same client instance when order was initiated, it doesn't require any parameters

- `orderRef` *Optional*. *str*. Can be found in response object from any order initiator methods. If given then corresponding order result will be requested. Usefull when the method is being used from different client instance than where the order was started.
- `qrStartToken` *Optional*. *str*. Can be found in response object from any order initiator methods. If given, it will be used to calculate QR data.
- `qrStartSecret` *Optional*. *str*. Can be found in response object from any order initiator methods. If given, it will be used to calculate QR data.
- `order_time` *Optional*. *int*. Can be found in response object from any order initiator methods. If given, it will be used to calculate QR data.

**Return:** `BankIdCollectResponse`
<br/>

##### def cancel(orderRef: str=None):

Cancels an ongoing sign or auth order. If used from same client instance when order was initiated, it doesn't require any parameters

- `orderRef` *Optional*. *str*. Can be found in response object from any order initiator methods. If given then corresponding order result will be requested. Usefull when the method is being used from different client instance than where the order was started.

**Return:** `BankIdCancelResponse`

<br/>

### class BankIdBaseResponse()

`response`: *requests.Response*. object which was returned from sending the request.
`response_status`: *int*. Http response code of the response
`response_data`: *dict*. returned data in dict format
`url`: *str*. The full url where the request was sent

<br/>

### class BankIdStartResponse(BankIdBaseResponse):

`orderRef`: *str*. Used to collect the status of the order. Parsed from BankID response.
`autoStartToken`: *str*. Used to compile the start url. Parsed from BankID response.
`qrStartToken`: *str*. Used to compute the animated QR code. Parsed from BankID response.
`qrStartSecret`: *str*. Used to compute the animated QR code. Parsed from BankID response.
`order_time`: *int*. order time in seconds since the Epoch.

<br/>

### class BankIdPhoneStartResponse(BankIdBaseResponse):

`orderRef`: *str*. Used to collect the status of the order. Parsed from BankID response.

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

##### class BankIdCompletionData()
`user`: *BankIdCompletionUserData*. Authenticated user information.
`device`: *BankIdCompletionDeviceData*. Authenticated user's device information.
`bankIdIssueDate`: *datatime*. The date the BankID was issued to the user.
`stepUp`: *str*. Information about extra verifications that were part of the transaction.
`signature`: *str*. The signature as described in the BankID Signature Profile specification. Base64-encoded.
`ocspResponse`: *str*. The OCSP response. Base64-encoded. The OCSP response is signed by a certificate that has the same issuer as the certificate being verified. The OSCP response has an extension for Nonce. The nonce is calculated as:
- SHA-1 hash over the base 64 XML signature encoded as UTF-8.
- 12 random bytes is added after the hash.
- The nonce is 32 bytes (20 + 12).
`json`: *dict*. Completion data in dict format.

##### class BankIdCompletionUserData()
`personalNumber`: *str*. The personal identity number.
`name`: *str*. The given name and surname of the user.
`givenName`: *str*. The given name of the user.
`surname`: *str*. The surname of the user.

##### class BankIdCompletionDeviceData()
`ipAddress`: *str*. The IP address of the user agent as the BankID server discovers it. When an order is started with autoStartToken the RP can check that this match the IP they observe to ensure session fixation String.
`uhi`: *str*. Unique hardware identifier for the users device.

<br/>

#### class BankIdCancelResponse(BankIdBaseResponse)
 ...
