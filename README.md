# bankid-6

## Quick Start

`BankIdClient` provides most of the functionality for BankID authentication process.

* The process is started by one of the start methods (`auth`, `sign`, `phone_auth`, `phone_sign`). 
* Any progress information can be found by `collect` method.
* Optionally the process can be terminated by `cancel` method.

These methods' functionality, parameters and return values are aligned with BankId's documentation. See API Reference part for information.

Example for test enviroment:
```
>>> from bankid6 import BankIdClient
>>> bankid_client = BankIdClient()
>>> bankid_client.auth('192.168.0.1')
<class 'src.bankid6.handlers.BankIdStartResponse'> response status: 200
response data: {"orderRef": "ccc9b028-4c83-49f8-b5ae-a3bac54a7427", "autoStartToken": "96c45dea-d14c-4bc5-bf30-db4015d39da9", "qrStartToken": "d550a68e-1e4d-4d66-8dce-3c6497c8da73", "qrStartSecret": "4b3bba21-ebaa-4bf4-8856-e66271550b78"}
>>> bankid_client.collect()
<class 'src.bankid6.handlers.BankIdCollectResponse'> response status: 200;
response data: {"orderRef": "ccc9b028-4c83-49f8-b5ae-a3bac54a7427", "status": "pending", "hintCode": "outstandingTransaction"}
>>> bankid_client.cancel()
<class 'src.bankid6.handlers.BankIdCancelResponse'> response status: 200;
response data: {}
```

For production environmet instantiate `BankIdClient` as:
```
>>> bankid_client = BankIdClient(prod_env=True, cert_pem=<filepath>, key_pem='<filepath>', ca_pem=<filepath>)
```
`cert_pem` represents the file path to the certificate, `key_pem` is the file path to the certificate's private key, and `ca_pem` denotes the file path to the CA Root Certificate, all of which are acquired from BankID.
Test certificates are provided within the package. However, in the case of a non-production environment (`prod_env=False`, which is the default for `prod_env`), any of the supplied certificates will be utilized.


#### Method Parameters and Return Values
All the start methods (`auth`, `sign`, `phone_auth`, `phone_sign`) has required or optionals parameter exactly described in bankid documentation. `collect` and `cancel` takes some optional parameters to be used form a different `BankIdClient` instance. These parameters are validated and sent as the data of the request to the BankID. Some parameters are simplified for easy use. e.g when `userVisibleDataFormat` paramater is set to 'True', it set's the value 'simpleMarkdownV1'.

All the methods return object that has parent class `BankIdBaseResponse`. The return object parses any returned data from BankID and makes available as attribute with same key name. e.g if Bankid returns `{'orderRef': 'some value'}` then the returned object will contain attribute `orderRef` with same value. It also preserves the nestesed structure of returned value.
The difference between naming `orderRef` and `order_time` attribute is `orderRef` comes from BankID and `order_time` is created by the package.
The returned objects are:
- `auth`, `sign` methods return `BankIdStartResponse`
- `phone_auth` and `phone_sign` methods return `BankIdPhoneStartResponse`
- `collect` method returns `BankIdCollectResponse`
- `cancel` method returns `BankIdCancelResponse` object.

See API Reference Section for full documentation of parameters and return values


#### Decoupling Start and Collect
The `collect` and `cancel` methods optionally takes `orderRef` parameter which can be used if you want to start the bankId process in one place and collect in another. 
``` 
>>> bankid_start = BankIdClient().phone_auth('192.168.0.1')
>>> BankIdClient().collect(orderRef=bankid_start.orderRef)
>>> BankIdClient().cancel(orderRef=bankid_start.orderRef)
```

The collect method also takes `qrStartToken`, `qrStartSecret` and `order_time` parameters to generate qr data. These values can be found in the attributes of `BankIdStartResponse` object (returned from `auth` and `sign`) with exact same name.
``` 
>>> bs = BankIdClient().phone_auth('192.168.0.1')
>>> bankid_collect = BankIdClient().collect(orderRef=bs.orderRef, qrStartToken=bs.qrStartToken, qrStartSecret=bs.qrStartSecret, order_time=bs.order_time)
>>> bankid_collect.qr_data
```

#### Showing QR code
`BankIdStartResponse` (returned from `auth` and `sign`) and `BankIdCollectResponse` (returned from `collect`) both contains `qr_data` to easily populate QR Code
```
>>> bankid_client = BankIdClient()
>>> bankid_start = bankid_client.phone_auth('192.168.0.1')
>>> bankid_start.qr_data
>>> bankid_collect = bankid_client.collect()
>>> bankid_collect.qr_data
```

The `qr_data` attribute in `collect` method is available if 
- the authentication process is started by same `BankIdClient` object's `auth` and `sign` method.
- Optional parameters `qrStartToken`, `qrStartSecret` and `order_time` are provided in decoupled mode.


#### Launching BankId App

`BankIdStartResponse` provies `launch_url` method returns the url to launch the bankid app. It takes an optional parameter `redirect` (default to null) that indicates redirect url after bankid is complete.
```
>>> bankid_start = BankIdClient().phone_auth('192.168.0.1')
>>> bankid_start.launch_url()
>>> bankid_start.launch_url('https://www.google.com')
```

The `launch_url` depends on the `is_mobile` (defalt to False) parameter of `BankIdClient`. This indicates if the process is running from a mobile of PC.
```
>>> bankid_start = BankIdClient(is_mobile=True).phone_auth('192.168.0.1')
>>> bankid_start.launch_url()
```

`autoStartToken` of `BankIdStartResponse` (returned from `auth` and `sign`) contains the autoStartToken returned from bankid.

#### Collecting Process Result

`BankIdCollectResponse` object (returned from `collect` method) provides information about authentication process result. Use it's `status` attribute to perform actions on different statuses. You can check the status against attribute of `CollectStatuses` class.
```
>>> bankid_collect = bankid_client.collect()
>>> from bankid6 import CollectStatuses
>>> print('Process Complete') if bankid_collect.status == CollectStatuses.complete else print('Something Else')
```

It also has `message` attribute which contains message to the customer. A message is depends of the bankid is being used and the language. So each message is a json/dict constructed like this:
```json
{
    "qrcode": {
        "swedish": "",
        "english": ""
    },
    "onfile": {
        "swedish": "",
        "english": ""
    }
} 
```

the `qrcode` means the use is staring the bankid process using scanning QR code. The `onfile` means the custumer with auto starting the bankid application on current device to start the process.
You can use `UseTypes` and `Languages` classes to get the appropriate message so that you don't have to memorize these keywords.
```
>>> bankid_collect = bankid_client.collect()
>>> from bankid6 import UseTypes, Languages
>>> print(bankid_collect.message[UseTypes.qrcode][Languages.en])
```

#### Exceptions

All methods in `BankIdClient` can raise `BankIdError` and `BankIdValidationError`. 

`BankIdError` is raised when a request is made to BankID server and it returned an error. It has `message` attribute with structure like:
```json
{
    "swedish": "",
    "english": ""
}
```
If the message is available, then it means that the message needs to be shown to the customer and nothing else. When it's not available, `reason` and `action` attribute can describe why error occoured and what need's to be done.


`BankIdValidationError` is raised if any parameter validation before sending the request is wrong.


## Sample Auth Script

.

## API Reference

### class BankIdClient()

#### def __init__(self, prod_env: bool=False, cert_pem: str=None, key_pem: str=None, ca_pem: str=None, request_timeout: int=None, messages: Messages=Messages, is_mobile: bool=False)

**Parameters:**
- `prod_env` indicates if it's a production environment. Test or prod urls are chosen based on this. If it is `True` then `key_pem`, `cert_pem` and `ca_pem` are required. Otherwise test certificates which are already included in the package will be used. Any or all of the certificates can also be provided when the value is `False`
- `cert_pem` file path of the certificate file
- `key_pem` file path of the private key of the certificate.
- `ca_pem` file path of CA certificate file
- `request_timeout` number of seconds to wait for response
- `messages` class or subclass of `Messages` class to override existing message
- `is_mobile` if it's being used in a mobile device.

#### def auth(endUserIp: str, requirement: dict=None, userVisibleData: str=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None):

Starts the bankid auth process. Use this when only user authentication is needed.

**Parameters:**
- `endUserIp` Required. ip address of the end user as string.
- `requirement` Optional. Requirements dictionary on how the auth order must be performed. See BankID documentation section Requirements below for more details. 
- `userVisibleData` Optional. Text displayed to the user. Takes a python string and makes it encoded as UTF-8 and then base 64 encoded. max 500 characters after 64 encoding.
- `userNonVisibleData` Optional. Text that is not displayed to the user. Takes a python string and makes it encoded as UTF-8 and then base 64 encoded. max 500 characters after 64 encoding.
- `userVisibleDataFormat` Optional. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

**Return:** `BankIdStartResponse`

#### def sign(endUserIp: str, userVisibleData: str, requirement: dict=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None)

Starts the bankid sign process. Use this when user is authenticated to sign something.

**Parameters:**
- `endUserIp` Required. ip address of the end user as string.
- `userVisibleData` Required. Text displayed to the user. Takes a python string and makes it encoded as UTF-8 and then base 64 encoded. max 500 characters after 64 encoding.
- `requirement` Optional. Requirements dictionary on how the auth order must be performed. See BankID documentation section Requirements below for more details. 
- `userNonVisibleData` Optional. Text that is not displayed to the user. Takes a python string and makes it encoded as UTF-8 and then base 64 encoded. max 500 characters after 64 encoding.
- `userVisibleDataFormat` Optional. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

**Return:** `BankIdStartResponse`

#### def phone_auth(personalNumber: str, callInitiator: str, requirement: dict=None, userVisibleData: str=None, userNonVisibleData: str=None, userVisibleDataFormat: Union[str, True]=None)

Initiates an authentication order when the user is talking to the RP over the phone. 

**Parameters:**
- `personalNumber` Required. String. Any valid personal number of the user. It's converted to 12 digit before adding to in the request.
- `callInitiator` Required. String choice between 'user' or 'RP'.
- `requirement` Optional. Requirements dictionary on how the auth order must be performed. See BankID documentation section Requirements below for more details. 
- `userVisibleData` Optional. Text displayed to the user. Takes a python string and makes it encoded as UTF-8 and then base 64 encoded. max 500 characters after 64 encoding.
- `userNonVisibleData` Optional. Text that is not displayed to the user. Takes a python string and makes it encoded as UTF-8 and then base 64 encoded. max 500 characters after 64 encoding.
- `userVisibleDataFormat` Optional. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

**Return:** `BankIdPhoneStartResponse`

#### def phone_sign(personalNumber, callInitiator, userVisibleData, requirement=None, userNonVisibleData=None, userVisibleDataFormat=None)

Initiates an signing order when the user is talking to the RP over the phone.

**Parameters:**
- `personalNumber` Required. String. Any valid personal number of the user. It's converted to 12 digit before adding to in the request.
- `callInitiator` Required. String choice between 'user' or 'RP'.
- `userVisibleData` Required. Text displayed to the user. Takes a python string and makes it encoded as UTF-8 and then base 64 encoded. max 500 characters after 64 encoding.
- `requirement` Optional. Requirements dictionary on how the auth order must be performed. See BankID documentation section Requirements below for more details. 
- `userNonVisibleData` Optional. Text that is not displayed to the user. Takes a python string and makes it encoded as UTF-8 and then base 64 encoded. max 500 characters after 64 encoding.
- `userVisibleDataFormat` Optional. The value can be set to "simpleMarkdownV1" or True. If it's True then the value is set to "simpleMarkdownV1".

**Return:** `BankIdPhoneStartResponse`

#### def collect(orderRef: str=None, qrStartToken: str=None, qrStartSecret: str=None, order_time: int=None)

Collect the result of the `auth`, `sign`, `phone_auth` or `phone_sign` methods. If used from same client instance when order was initiated, it doesn't require any parameters

- `orderRef` Optional. String. If given then corresponding order result will be requested. Usefull when the method is being used from different client instance than where the order was started.
- `qrStartToken`, `qrStartSecret`, `order_time` Optional. If given these are used to calculated QR data. Usefull when the method is being used from different client instance than where the order was started.

**Return:** `BankIdCollectResponse`

#### def cancel(orderRef: str=None):

Cancels an ongoing sign or auth order. If used from same client instance when order was initiated, it doesn't require any parameters

- `orderRef` Optional. String. If given then corresponding order will be cancelled. Usefull when the method is being used from different client instance than where the order was started.

**Return:** `BankIdCancelResponse`