from bankid6.message import MesssageDetail, get_bankid_collect_message, Messages
from bankid6 import Languages, HintCodes, CollectStatuses, UseTypes


def test_MessageDetail():
    md = MesssageDetail('swedish msg', 'english msg', help_text='test msg')
    jm = md.json()
    assert type(jm) == dict
    assert jm == {Languages.en: 'english msg', Languages.sv: 'swedish msg'}


def test_get_bankid_collect_message():
    msg = get_bankid_collect_message(CollectStatuses.pending, HintCodes.outstandingTransaction)
    assert msg[UseTypes.qrcode] == Messages.RFA1.json()
    assert msg[UseTypes.onfile] == Messages.RFA13.json()

    msg = get_bankid_collect_message(CollectStatuses.pending, HintCodes.started, is_mobile=True)
    assert msg[UseTypes.qrcode] == Messages.RFA15B.json()
    assert msg[UseTypes.onfile] == Messages.RFA15B.json()

    msg = get_bankid_collect_message(CollectStatuses.pending, HintCodes.started, is_mobile=False)
    assert msg[UseTypes.qrcode] == Messages.RFA15A.json()
    assert msg[UseTypes.onfile] == Messages.RFA15A.json()

    msg = get_bankid_collect_message(CollectStatuses.failed, HintCodes.userCancel, is_mobile=True)
    assert msg[UseTypes.qrcode] == Messages.RFA6.json()
    assert msg[UseTypes.onfile] == Messages.RFA6.json()

    msg = get_bankid_collect_message(CollectStatuses.failed, HintCodes.userCancel, is_mobile=False)
    assert msg[UseTypes.qrcode] == Messages.RFA6.json()
    assert msg[UseTypes.onfile] == Messages.RFA6.json()

    msg = get_bankid_collect_message(CollectStatuses.failed, HintCodes.startFailed, is_mobile=True)
    assert msg[UseTypes.qrcode] == Messages.RFA17B.json()
    assert msg[UseTypes.onfile] == Messages.RFA17A.json()

    msg = get_bankid_collect_message(CollectStatuses.failed, HintCodes.startFailed, is_mobile=False)
    assert msg[UseTypes.qrcode] == Messages.RFA17B.json()
    assert msg[UseTypes.onfile] == Messages.RFA17A.json()

    # default message failed
    msg = get_bankid_collect_message(CollectStatuses.failed, HintCodes.userDeclinedCall, is_mobile=False)
    assert msg[UseTypes.qrcode] == Messages.RFA22.json()
    assert msg[UseTypes.onfile] == Messages.RFA22.json()

    # default message pending
    msg = get_bankid_collect_message(CollectStatuses.pending, HintCodes.userCallConfirm, is_mobile=False)
    assert msg[UseTypes.qrcode] == Messages.RFA21.json()
    assert msg[UseTypes.onfile] == Messages.RFA21.json()
