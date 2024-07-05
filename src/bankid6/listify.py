class CollectStatuses():
    pending = 'pending'
    failed = 'failed'
    complete = 'complete'


class HintCodesPending():
    outstandingTransaction = "outstandingTransaction"
    noClient = "noClient"
    started = "started"
    userMrtd = "userMrtd"
    userCallConfirm = "userCallConfirm"
    userSign = "userSign"
    default = "default"


class HintCodesFailed():
    expiredTransaction = "expiredTransaction"
    certificateErr = "certificateErr"
    userCancel = "userCancel"
    cancelled = "cancelled"
    startFailed = "startFailed"
    userDeclinedCall = "userDeclinedCall"
    notSupportedByUserApp = "notSupportedByUserApp"
    transactionRiskBlocked = "transactionRiskBlocked"
    default = "default"


class HintCodes(HintCodesPending, HintCodesFailed):
    pass


class UseTypes():
    qrcode = 'qrcode'
    onfile = 'onfile'


class Languages():
    sv = 'swedish'
    en = 'english'
