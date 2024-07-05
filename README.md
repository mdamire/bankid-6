# bankid6

<br/>

## Overview

A complete implementation of Swedish BankID authentication system version 6.  It includes initiating/collecting/canceling authentication orders, user Messages and exception handling according to [BankID Documentaion](https://www.bankid.com/en/utvecklare/guider/teknisk-integrationsguide/rp-introduktion). This package is easy to use while having all the functionalities of BankId API.
<br/>

**Installation:**

```
pip install bankid6
```
Supports and tested on python version 3.6 and later.
<br/>

This documentation is divided into three sections: ***User Guide***, ***Sample Script*** and ***API Reference***.

* The ***User Guide*** section offers a step-by-step guide covering all functionalities.
* The ***Sample Script*** section demonstrates the authentication process via python script.
* The ***API Reference*** section provides detailed descriptions of each object.

Follow the ***User Guide*** for a guided experience, and refer to the ***API Reference*** for in-depth information about specific objects. The ***Sample Script*** provides a quick overview of basic functionalities, which may suffice in many cases.

<br/>
<br/>

## A. User Guide


### 1. `BankIdClient` Class

The `BankIdClient` class provides methods to initiate authentication or signing orders, collect order results, and cancel orders. It can be instantiated for both production and test environments, with configurations based on the specified environment.

#### Initializing BankIdClient

- **Production Environment:** Set the `prod_env` parameter to `True` and provide file paths for the certificate, private key, and CA certificate.
    ```python
    from bankid6 import BankIdClient

    bankid_client = BankIdClient(
            prod_env=True,
            cert_pem='<certificate_filepath>',
            key_pem='<private_key_filepath>',
            ca_pem='<ca_certificate_filepath>'
        )
    ```

- **Test Environment:** Certificates for the test environment are included in the package, so you can omit certificate-related parameters. The `prod_env` parameter defaults to `False`, allowing instantiation without any parameters for testing purposes.
    ```python
    bankid_client = BankIdClient()
    ```

#### Additional Parameters

- **is_mobile:** This parameter defaults to `False`. Set it to `True` to render correct messages and URLs for launching the app on mobile devices.
    ```python
    bankid_client = BankIdClient(is_mobile=True)
    ```
- **messages:** This parameter is used to add custom message when collecting an order result. Further information will be covered at a later point.
<br/>

### 2. Authentication or Signing Order

The `BankIdClient` offers four methods to start authentication or signing orders: `auth`, `sign`, `phone_auth`, and `phone_sign`. These methods correspond to the endpoints of the BankId API.

- **`auth` and `sign` Methods:**
    These methods initiate authentication and signing orders, respectively. They return a `BankIdStartResponse` object, which contains attributes to easily get the data for QR code and the URL for launching the BankID app on the current device.
    
    ```python
    >>> bankid_client = BankIdClient()
    >>> start_response = bankid_client.auth('192.168.0.1')  # Takes IP of end user
    
    >>> start_response.qr_data                              # Calculated data to create QR code
    'bankid.c03da000-d5de-4435-b81b-66154960784d.8.7a7f4a36307cb8d8ddb4fe86116764819def4c32c55d1ba792e6e4117be9a5a1'
    
    >>> start_response.launch_url()                         # Depends on is_mobile parameter of the BankIdClient
    'bankid:///?autostarttoken=aaba5bef-1066-42da-b6c6-0730b8c53997&redirect=null'
    
    >>> start_response.launch_url('https://www.google.com') # Takes a redirect URL as parameter
    'bankid:///?autostarttoken=aaba5bef-1066-42da-b6c6-0730b8c53997&redirect=https%3A%2F%2Fwww.google.com'
    
    >>> [attr for attr in dir(start_response) if not attr.startswith('_')]
    ['autoStartToken', 'data', 'launch_url', 'orderRef', 'order_time', 'qrStartSecret', 'qrStartToken', 'qr_data', 'response', 'status_code', 'url']
    ```
    Subsequent QR data can be found in the response of the `collect` method or from the standalone `generate_qr_data` function.
    ```python
    >>> from bankid6 import generate_qr_data
    >>> generate_qr_data(start_response.order_time, start_response.qrStartToken, start_response.qrStartSecret)
    'bankid.c03da000-d5de-4435-b81b-66154960784d.250.16f0f42bb4f1a99d41a31e38cd54866fce5a193e277f4d48339a7579ac51fe4e'
    ```

- **`phone_auth` and `phone_sign` Methods:**
    These methods start authentication and signing orders while the customer is on the phone. You need to pass a personal number, and the BankID will send the request to the customer's BankID app. These methods return a `BankIdPhoneStartResponse` object.
    
    ```python
    >>> phone_start_response = BankIdClient().phone_auth('199002113166', callInitiator="RP")
    >>> [attr for attr in dir(phone_start_response) if not attr.startswith('_')]
    ['data', 'orderRef', 'response', 'status_code', 'url']
    ```
<br>

Both `sign` and `phone_sign` methods require the `userVisibleData` parameter.
```python
>>> BankIdClient().sign('192.168.0.1', userVisibleData="Hello! Sign this test document")
<class 'bankid6.handlers.BankIdStartResponse'> response status: 200;
response data: {"orderRef": "6eaf4368-22ae-4309-8768-f58b772d1617", "autoStartToken": "3d973332-8abe-4273-b292-b16c975a1a39", "qrStartToken": "29d0b198-487d-42b8-91a8-c63fc94a2733", "qrStartSecret": "a611ccd5-5940-4160-9fde-20a251716bfb"}
```

All of these four methods have required or optional parameters exactly as described in the BankID documentation. These parameters are validated and processed as BankID requires and sent as the data of the request to the BankID.

The returned objects derived from `BankIdBaseResponse` parse the BankID response and create attributes with the same names as the keys in response data. Typically, you won't need to directly access the responses of these four methods, as the necessary attributes are stored in the object when you use the `collect` method from the same object.

See the API Reference section for comprehensive documentation detailing parameters and return values.
<br/>

### 3. Order Result Collection

To retrieve the result of an order, use the `collect` method of the `BankIdClient` object.

```python
>>> from bankid6 import BankIdClient
>>> bankid_client = BankIdClient()

>>> bankid_client.auth('192.168.0.1')
<class 'bankid6.handlers.BankIdStartResponse'> response status: 200
response data: {"orderRef": "ccc9b028-4c83-49f8-b5ae-a3bac54a7427", "autoStartToken": "96c45dea-d14c-4bc5-bf30-db4015d39da9", "qrStartToken": "d550a68e-1e4d-4d66-8dce-3c6497c8da73", "qrStartSecret": "4b3bba21-ebaa-4bf4-8856-e66271550b78"}

>>> bankid_client.collect()
<class 'bankid6.handlers.BankIdCollectResponse'> response status: 200;
response data: {"orderRef": "ccc9b028-4c83-49f8-b5ae-a3bac54a7427", "status": "pending", "hintCode": "outstandingTransaction"}
```
<br>

The `collect` method returns a `BankIdCollectResponse` object, derived from the `BankIdBaseResponse` class, which parses data returned from the BankID `/collect` endpoint.

```python
>>> collect_response = bankid_client.collect()
>>> collect_response.status                             # Retrieve BankID status from response data
'pending'
>>> collect_response.qr_data                            # Calculate QR data based on current time             
'bankid.d9c9339c-b9d3-48a2-8289-8d66e1d28a08.21.941023af5b86d5b16aaa226ad7130ee08a1dcdca89e199639a3986336a0569fb'
>>> from bankid6 import CollectStatuses
>>> collect_response.status == CollectStatuses.pending   # Use predefined constants for status comparison
True
```

According to BankID documentation, the `completionData` attribute (object of `BankIdCompletionData`) provides information when the status is "complete".

```python
>>> collect_response = bankid_client.collect()
>>> print(collect_response.completionData.user.personalNumber) if collect_response.status == CollectStatuses.complete else print(collect_response.hintCode)
```
<br>

You can decouple the `collect` method from order initiation methods. If executed from a different `BankIdClient` object, the method requires specific parameters, as shown below. These parameters are obtained from the response object returned by the order initiation methods described in the previous section.

```python
>>> start_response = BankIdClient().auth('192.168.0.1')
>>> start_response.qr_data 
'bankid.d9c9339c-b9d3-48a2-8289-8d66e1d28a08.21.941023af5b86d5b16aaa226ad7130ee08a1dcdca89e199639a3986336a8dg3b3'

>>> collect_response = BankIdClient().collect(
        orderRef=start_response.orderRef, 
        qrStartToken=start_response.qrStartToken, 
        qrStartSecret=start_response.qrStartSecret, 
        order_time=start_response.order_time
    )
>>> collect_response.qr_data
'bankid.d9c9339c-b9d3-48a2-8289-8d66e1d28a08.21.941023af5b86d5b16aaa226ad7130ee08a1dcdca89e199639a3986336a0569fb'
```

The `orderRef` parameter locates the order, while `qrStartToken`, `qrStartSecret`, and `order_time` parameters calculate the QR code. Access to the `qr_data` attribute in the `BankIdCollectResponse` object is available if the `collect` method is called from the same client where the order was initiated, or if these parameters are provided.
<br>

#### User Message

The `BankIdCollectResponse` also includes a `message` attribute, which provides user messages based on the BankID documentation when the status is 'pending' or 'failed' (otherwise `None`). Each message is structured as follows:

```python
{
    "qrcode": {
        "swedish": "Svensk massage",
        "english": "English Message"
    },
    "onfile": {
        "swedish": "Svensk massage",
        "english": "English Message"
    }
} 
```

Since the method of starting authentication (via QR code or app on the same device) and the preferred language are user choices, you need to dynamically extract the correct message at runtime. This can be done conveniently using the `UseTypes` and `Languages` classes.

```python
from bankid6 import UseTypes, Languages

... # initialize authentication order like shown before

cr = bankid_client.collect()
if cr.status in [CollectStatuses.pending, CollectStatuses.failed]:
    print(cr.message[UseTypes.qrcode][Languages.en])    # prints 'Start your BankID app.'
```

You can also subclass `Messages`, override its existing messages, and pass it as a parameter to `BankIdClient`. This is useful if you want to change the message to html format. Each message in the `Messages` class is an attribute starting with 'RFA', as per BankID documentation.

```python
from bankid6 import Messages

# Print the help text for RFA1
print(Messages.RFA1.help_text) # prints 'status=pending, hintCode=outstandingTransaction, hintCode=noClient'

# Example of customizing Messages
class MyMessages(Messages):
    RFA1 = {'test': 'yes'}
    RFA13 = ('<h3>swedish message<h3>', '<h3>english message</h3>')

bankid_client = BankIdClient(messages=MyMessages)
```

In `MyMessages`, values can be dictionaries or tuples containing Swedish and English messages. If the value is a dictionary, newly added keys are accessible from the `message` attribute of the `BankIdCollectResponse` object.

For some hint codes where the BankID documentation does not provide a user message, the `message` attribute will contain a default user message. You can define your own message by checking the `status` attribute against the `CollectStatuses` class attributes and the `hintCode` attribute against the `HintCodes` class attributes.
```python
from bankid6 import BankIdClient, CollectStatuses, HintCodes

... # initialize authentication order like shown before

cr = bankid_client.collect()
if cr.status == CollectStatuses.failed and cr.hintCode == HintCodes.userDeclinedCall:
    custome_message = "Customer didn't verify the call in action" # Your custom message
```

<br/>

### 4. Cancel Order
Use `cancel` mothod of `BankIdClient` object to cancel the order. The method returns `BankIdCancelResponse` object.
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

### 5. Exceptions

All methods in `BankIdClient` can raise `BankIdError` or `BankIdValidationError`. See the code in Sample Script section to understand how these exceptions should be handeled.

- **`BankIdError` Exception**:
    `BankIdError` is raised when a request is made to BankID server and it returns an error. In some cases, BankId documentation provides user message which is available in `message` attribute. The `message` has a structure like this:
    ```json
    {
        "swedish": "",
        "english": ""
    }
    ```
    If the message is available, it indicates that the message should be presented to the customer without any additional action required. Otherwise, the `reason` and `action` attributes can provide information on why the error occurred and what steps need to be taken to address it according to BankID documentation. You can log these attribute values to understand the error.
    Attribute `response_data` has the data received from BankID in dict format. See Api Reference section for more functionalities.

- **`BankIdValidationError` Exception:**
    `BankIdValidationError` is raised before sending the request to BankID if any parameter is invalid.

<br/>
<br/>
<br/>

## B. Sample Script

```python
import time
from bankid6 import BankIdClient, CollectStatuses, UseTypes, Languages, BankIdError, HintCodes


bankid_client = BankIdClient()

try:
    start_response = bankid_client.auth('192.168.0.1')
except BankIdError as bie:
    if bie.message:
        print("User Message: ", bie.message[Languages.en])
    else:
        raise Exception(f"Fatal error. reason: {bie.reason}; action needed: {bie.action}; response data: {bie.response_data}; response status: {bie.response_status}") from bie

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
            raise Exception(f"Fatal error. reason: {bie.reason}; action needed: {bie.action}; response data: {bie.response_data}; response status: {bie.response_status}") from bie


    if collect_response.status == CollectStatuses.complete:
        print('Authenticated by: ', collect_response.completionData.user.name)
        break

    else:
        if collect_response.hintCode == HintCodes.outstandingTransaction:
            print('QR data: ', collect_response.qr_data)
        
        print("User Message: ", collect_response.message[UseTypes.qrcode][Languages.en])
        
        if collect_response.status == CollectStatuses.failed:
            break

```

<br/>
<br/>
<br/>

## C. API Reference


#### class BankIdClient()

**def __init__(self, prod_env: bool=False, cert_pem: str=None, key_pem: str=None, ca_pem: str=None, request_timeout: int=None, messages: Messages=Messages, is_mobile: bool=False)**

- **Parameters:**
    - `prod_env` indicates if it's a production environment. Test or prod urls are chosen based on this. If it is `True` then `key_pem`, `cert_pem` and `ca_pem` are required. Otherwise test certificates which are already included in the package will be used. Any or all of the certificates can also be provided when the value is `False`
    - `cert_pem` file path of the certificate file
    - `key_pem` file path of the private key of the certificate.
    - `ca_pem` file path of CA certificate file
    - `request_timeout` number of seconds to wait for response
    - `messages` class or subclass of `Messages` class to override existing message
    - `is_mobile` if it's being used in a mobile device.
<br/>

**def auth(endUserIp: str, requirement: dict=None, userVisibleData: str=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None):**

Starts the BankID auth process. Use this when only user authentication is needed.

- **Parameters:**
    - `endUserIp` ***Required***. *str*. The user IP address as seen by RP. IPv4 and IPv6 are allowed.
    - `requirement` *Optional*. *dict | object that can be converted to dict*. Requirements dictionary on how the auth order must be performed. See BankID documentation for more details. 
    - `userVisibleData` *Optional*. *str*. Text displayed to the user during authentication with BankID. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
    - `userNonVisibleData` *Optional*. *str*. Text that is not displayed to the user. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
    - `userVisibleDataFormat` *Optional*. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

- **Return:** `BankIdStartResponse`
<br/>

**def sign(endUserIp: str, userVisibleData: str, requirement: dict=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None)**

Starts the BankID sign process. Use this when user is authenticated to sign something.

- **Parameters:**
    - `endUserIp` ***Required***. *str*. The user IP address as seen by RP. IPv4 and IPv6 are allowed.
    - `userVisibleData` ***Required***. *str*. Text displayed to the user during authentication with BankID. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
    - `requirement` *Optional*. *dict | object that can be converted to dict*. Requirements dictionary on how the auth order must be performed. See BankID documentation for more details. 
    - `userNonVisibleData` *Optional*. *str*. Text that is not displayed to the user. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
    - `userVisibleDataFormat` *Optional*. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

- **Return:** `BankIdStartResponse`
<br/>

**def phone_auth(personalNumber: str, callInitiator: str, requirement: dict=None, userVisibleData: str=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None)**

Initiates an authentication order when the user is talking to the RP over the phone. 

- **Parameters:**
    - `personalNumber` ***Required***. *str*. Any valid 12 digit personal number of the user.
    - `callInitiator` ***Required***. *str*. choice between 'user' or 'RP'.
    - `requirement` *Optional*. *dict | object that can be converted to dict*. Requirements dictionary on how the auth order must be performed. See BankID documentation for more details. 
    - `userVisibleData` *Optional*. *str*. Text displayed to the user during authentication with BankID. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
    - `userNonVisibleData` *Optional*. *str*. Text that is not displayed to the user. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
    - `userVisibleDataFormat` *Optional*. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

- **Return:** `BankIdPhoneStartResponse`
<br/>

**def phone_sign(personalNumber, callInitiator, userVisibleData, requirement=None, userNonVisibleData=None, userVisibleDataFormat=None)**

Initiates an signing order when the user is talking to the RP over the phone.

- **Parameters:**
    - `personalNumber` ***Required***. *str*. Any valid 12 digit personal number of the user.
    - `callInitiator` ***Required***. *str*. choice between 'user' or 'RP'.
    - `userVisibleData` ***Required***. *str*. Text displayed to the user during authentication with BankID. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
    - `requirement` *Optional*. *dict | object that can be converted to dict*. Requirements dictionary on how the auth order must be performed. See BankID documentation for more details. 
    - `userNonVisibleData` *Optional*. *str*. Text that is not displayed to the user. Converted to UTF-8 encoded and then base 64 encoded string. 1 to 1500 characters after 64 encoding.
    - `userVisibleDataFormat` *Optional*. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

- **Return:** `BankIdPhoneStartResponse`
<br/>

**def collect(orderRef: str=None, qrStartToken: str=None, qrStartSecret: str=None, order_time: int=None)**

Collect the result of the `auth`, `sign`, `phone_auth` or `phone_sign` methods. If used from same client instance when order was initiated, it doesn't require any parameters

- **Parameters:**
    - `orderRef` *Optional*. *str*. Can be found in response object from any order initiator methods. If given then the corresponding order result will be requested. Useful when the method is being used from the different client instance than where the order was started.
    - `qrStartToken` *Optional*. *str*. Can be found in response object from any order initiator methods. If given, it will be used to calculate QR data.
    - `qrStartSecret` *Optional*. *str*. Can be found in response object from any order initiator methods. If given, it will be used to calculate QR data.
    - `order_time` *Optional*. *int*. Can be found in response object from any order initiator methods. If given, it will be used to calculate QR data.

- **Return:** `BankIdCollectResponse`
<br/>

**def cancel(orderRef: str=None):**

Cancels an ongoing sign or auth order. If used from same client instance when order was initiated, it doesn't require any parameters

- **Parameters:**
    - `orderRef` *Optional*. *str*. Can be found in response object from any order initiator methods. If given then the corresponding order result will be requested. Useful when the method is being used from the different client instance than where the order was started.

- **Return:** `BankIdCancelResponse`

<br/>
<br/>

### class BankIdBaseResponse()
- **Attributes**:
    - `response`: *requests.Response*. object which was returned from sending the request.
    - `status`: *int*. Http response code of the response
    - `data`: *dict*. returned data in dict format
    - `url`: *str*. The full url where the request was sent

<br/>
<br/>

### class BankIdStartResponse(BankIdBaseResponse):
- **Attributes**:
    - `orderRef`: *str*. Used to collect the status of the order. Parsed from BankID response.
    - `autoStartToken`: *str*. Used to compile the start url. Parsed from BankID response.
    - `qrStartToken`: *str*. Used to compute the animated QR code. Parsed from BankID response.
    - `qrStartSecret`: *str*. Used to compute the animated QR code. Parsed from BankID response.
    - `order_time`: *int*. order time in seconds since the Epoch.

<br/>
<br/>

### class BankIdPhoneStartResponse(BankIdBaseResponse):
- **Attributes**:
    - `orderRef`: *str*. Used to collect the status of the order. Parsed from BankID response.

<br/>
<br/>

### class BankIdCollectResponse(BankIdBaseResponse)
- **Attributes**:
    - `orderRef`: *str*. Used to collect the status of the order. Parsed from BankID response.
    - `status`: *str*. 'pending' | 'complete' | 'failed'. Parsed from BankID response.
    - `hintCode`: *str*. Only present for pending and failed orders. Parsed from BankID response.
    - `completionData`: *BankIdCompletionData*. Only present for complete orders. Parsed from BankID response.
    - `message`: *dic*. User message according to bankid documentation. which has following format:
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
- **Attributes**:
    - `user`: *BankIdCompletionUserData*. Authenticated user information.
    - `device`: *BankIdCompletionDeviceData*. Authenticated user's device information.
    - `bankIdIssueDate`: *datetime*. The date the BankID was issued to the user.
    - `stepUp`: *str*. Information about extra verifications that were part of the transaction.
    - `signature`: *str*. The signature as described in the BankID Signature Profile specification. Base64-encoded.
    - `ocspResponse`: *str*. The OCSP response. Base64-encoded. The OCSP response is signed by a certificate that has the same issuer as the certificate being verified. The OSCP response has an extension for Nonce. The nonce is calculated as:
        - SHA-1 hash over the base 64 XML signature encoded as UTF-8.
        - 12 random bytes are added after the hash.
        - The nonce is 32 bytes (20 + 12).
    - `json`: *dict*. Completion data in dict format.
<br/>
<br/>

### class BankIdCompletionUserData()
- **Attributes**:
    - `personalNumber`: *str*. The personal identity number.
    - `name`: *str*. The given name and surname of the user.
    - `givenName`: *str*. The given name of the user.
    - `surname`: *str*. The surname of the user.
<br/>
<br/>

### class BankIdCompletionDeviceData()
- **Attributes**:
    - `ipAddress`: *str*. The IP address of the user agent as the BankID server discovers it. When an order is started with autoStartToken the RP can check that this matchs the IP they observe to ensure session fixation String.
    - `uhi`: *str*. Unique hardware identifier for the user's device.
<br/>
<br/>

### class BankIdCancelResponse(BankIdBaseResponse)
***...***
<br/>
<br/>

### class BankIdError(Exception)
- **Attributes**:
    - `reason`: *str*. Reason of the exception according to the BankID Documentation
    - `action`: *str*. What action is needed for this exception according to BankID Documentation
    - `message`: *dict*. Message for users.
    - `errorCode`: *str*. Error code received in response data
    - `response`: *requests.Response*. object which was returned from sending the request.
    - `response_status`: *int*. Http response code of the response
    - `response_data`: *dict*. returned data in dict format
<br/>
<br/>

### class BankIdValidationError(Exception)
***...***

<br/>
