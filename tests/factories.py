from unittest.mock import MagicMock


def response_factory(status, data, text="test", url="test"):
    # Create a mock response object
    response_mock = MagicMock()

    # Set attributes of the response object as needed for testing
    response_mock.status_code = status
    response_mock.text = text
    response_mock.json.return_value = data
    response_mock.url = url

    return response_mock
