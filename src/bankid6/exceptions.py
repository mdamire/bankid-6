from .message import Messages, MesssageDetail


class BankIdError(Exception):
    def __init__(self, reason, action, message, error_code, response, response_status, response_data):
        self.reason = reason
        self.action = action
        self.message = message
        self.error_code = error_code
        self.response = response
        self.response_status = response_status
        self.response_data = response_data
        super().__init__(reason)


class ErrorDescription():
    def __init__(self, reason, action, message=None):
        self.reason = reason
        self.action = action
        if isinstance(message, MesssageDetail):
            self.message = message.json()
        else:
            self.message = message


known_400_errors = ["alreadyInProgress", "invalidParameters", "dummy"]


def get_error_description(status_code, error_code, messages:Messages):
    ErrorDescriptions = {
        400: {
            'alreadyInProgress': ErrorDescription(
                ("An auth or sign request with a personal number was sent, "
                "but an order for the user is already in progress. The order is aborted. "
                "No order is created.\n\nDetails are found in details."),
                ("RP must inform the user that an auth or sign order is already "
                "in progress for the user. Message RFA4 should be used."),
                messages.RFA4.json()
            ),
            'invalidParameters': ErrorDescription(
                ("Invalid parameter. Invalid use of method. Details are found in details.\n\n"
                "Potential causes:\n\n"
                "* Using an orderRef that previously resulted in a completed order. "
                "The order cannot be collected twice.\n\n"
                "Using an orderRef that previously resulted in a failed order. "
                "The order cannot be collected twice.\n\n"
                "Using an orderRef that is too old.\n\n"
                "Completed orders can only be collected up to 3 minutes and "
                "failed orders up to 5 minutes.\n\n"
                "Timed out orders due to never being picked up by the client "
                "are only available for collect for 3 min and 10 seconds.\n\n"
                "Using a different RP-certificate than the one used to create the order.\n\n"
                "Using too big content in the request.\n\n"
                "Using non-JSON in the request body."),
                ("RP must not try the same request again. This is an internal error "
                "within the RP's system and must not be communicated to the user "
                "as a BankID error.")
            ),
            'unknownError': ErrorDescription(
                ("We may introduce new error codes without prior notice. "
                "RP must handle unknown error codes in their implementations.\n\n"),
                ("If an unknown errorCode is returned, RP should inform the user. "
                "Message RFA22 should be used.\n\n"
                "RP should update their implementation to support the new "
                "errorCode as soon as possible."),
                messages.RFA22.json()
            )
        },
        401: {
            "unauthorized": ErrorDescription(
                "RP does not have access to the service.",
                ("RP must not try the same request again. This is an internal error within "
                "the RP's system and must not be communicated to the user as a BankID error.")
            )
        },
        403: {
            "unauthorized": ErrorDescription(
                "RP does not have access to the service.",
                ("RP must not try the same request again. This is an internal error within "
                "the RP's system and must not be communicated to the user as a BankID error.")
            )
        },
        404: {
            "notFound": ErrorDescription(
                "An erroneous URL path was used.",
                ("RP must not try the same request again. This is an internal error within "
                "the RP's system and must not be communicated to the user as a BankID error.")
            )
        },
        405: {
            "methodNotAllowed": ErrorDescription(
                "Only http method POST is allowed.",
                ("RP must not try the same request again. This is an internal error within the "
                "RP's system and must not be communicated to the user as a BankID error.")
            ),
            "<empty>": ErrorDescription(
                "Only http method POST is allowed.",
                ("RP must not try the same request again. This is an internal error within the "
                "RP's system and must not be communicated to the user as a BankID error.")
            ),
        },
        408: {
            "requestTimeout": ErrorDescription(
                "It took too long time to transmit the request.",
                ("RP must not automatically try again. This error may occur if the processing "
                "at RP or the communication is too slow. RP must inform the user. "
                "Message RFA5 should be used."),
                messages.RFA5.json()
            )
        },
        415: {
            "unsupportedMediaType": ErrorDescription(
                ("Adding a 'charset' parameter after 'application/json' is not allowed since "
                "the MIME type 'application/json' has neither optional nor required parameters."),
                ("RP must not try the same request again. This is an internal error within the "
                "RP's system and must not be communicated to the user as a BankID error.")
            )
        },
        500: {
            "internalError": ErrorDescription(
                "Internal technical error in the BankID system.",
                "RP must not automatically try again. RP must inform the user. Message RFA5 should be used.",
                messages.RFA5.json()
            )
        },
        503: {
            "maintenance": ErrorDescription(
                "The service is temporarily unavailable.",
                ("RP may try again without informing the user. If this error is returned repeatedly, "
                "RP must inform the user. Message RFA5 should be used."),
                messages.RFA5.json()
            )
        }
    }

    try:
        return ErrorDescriptions[status_code][error_code]
    except KeyError:
        return ErrorDescription(None, None, None)


def check_bankid_error(response, messages: Messages=Messages):
    try:
        response_data = response.json()
    except Exception:
        response_data = {}
    
    if not response.ok:
        error_code = response_data.get('errorCode', 'dummy')
        if response.status_code == 400 and error_code not in known_400_errors:
            error_code = 'unknownError'
        
        error_description = get_error_description(response.status_code, error_code, messages)

        raise BankIdError(
            reason=error_description.reason,
            action=error_description.action,
            message=error_description.message,
            response=response,
            response_status=response.status_code,
            response_data=response_data
        )
