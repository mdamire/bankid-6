from unittest.mock import MagicMock


def response_factory(status, data, text="test", url="test", ok=True):
    # Create a mock response object
    response_mock = MagicMock()

    # Set attributes of the response object as needed for testing
    response_mock.status_code = status
    response_mock.text = text
    response_mock.json.return_value = data
    response_mock.url = url
    response_mock.ok = ok

    return response_mock

TEST_START_RESPONSE_DATA = {
    'orderRef': '894c311b-0bcb-4d65-bb5b-7580c300f098',
    'autoStartToken': '79439e65-1862-4b27-aefb-dacdb9e62cba',
    'qrStartToken': 'c56e2cd6-c4da-45f1-a104-e59e7cc6d2fa',
    'qrStartSecret': '3cd671e5-3389-4134-9565-decc8388bc8c'
}
TEST_START_RESPONSE = response_factory(200, TEST_START_RESPONSE_DATA)

TEST_PHONE_START_RESPONSE_DATA = {
    'orderRef': '894c311b-0bcb-4d65-bb5b-7580c300f098'
}
TEST_PHONE_START_RESPONSE = response_factory(200, TEST_PHONE_START_RESPONSE_DATA)

TEST_COLLECT_DATA = {
    'orderRef': '00e1b699-1191-43aa-b09d-d95c1bfb4e69', 
    'status': 'pending', 
    'hintCode': 'outstandingTransaction'
}
TEST_COLLECT_RESPONSE = response_factory(200, TEST_COLLECT_DATA)

TEST_COLLECT_COMPLETE_DATA = {
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
TEST_COLLECT_COMPLETE_RESPONSE = response_factory(201, TEST_COLLECT_COMPLETE_DATA)

TEST_CANCEL_RESPONSE = response_factory(200, {})
