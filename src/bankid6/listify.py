class CollectStatuses():
    pending = 'pending'
    failed = 'failed'
    complete = 'complete'


class HintCodesPending():
    outstandingTransaction = "outstandingTransaction"
    noClient = "noClient"
    userSign = "userSign"
    started = "started"
    userMrtd = "userMrtd"
    default = "default"


class HintCodesFailed():
    userCancel = "userCancel"
    expiredTransaction = "expiredTransaction"
    certificateErr = "certificateErr"
    startFailed = "startFailed"
    default = "default"


class HintCodes(HintCodesPending, HintCodesFailed):
    pass


class UseTypes():
    qrcode = 'qrcode'
    onfile = 'onfile'


class Languages():
    sv = 'swedish'
    en = 'english'
