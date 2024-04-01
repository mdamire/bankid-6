from bankid6.exceptions import check_bankid_error, BankIdError
from .factories import response_factory


def test_check_bankid_error():
    try:
        check_bankid_error(response_factory(400, {'errorCode': 'alreadyInProgress'}, ok=False))
    except BankIdError as exc:
        assert isinstance(exc, BankIdError)
        assert exc.response_status == 400
        assert exc.errorCode == 'alreadyInProgress'
        assert isinstance(exc.reason, str)
        assert isinstance(exc.action, str)
        assert isinstance(exc.message, dict)
        assert isinstance(exc.response_data, dict)
    else:
        assert False
