from .listify import CollectStatuses, UseTypes, Languages


class MesssageDetail():
    def __init__(self, swedish, english, help_text="") -> None:
        self.swedish = swedish
        self.english = english
        self.help_text = help_text
    
    def json(self):
        return {
            Languages.sv: self.swedish,
            Languages.en: self.english,
        }


class Messages():
    RFA1 = MesssageDetail(
        "Starta BankID-appen.", 
        "Start your BankID app.",
        help_text="status=pending, hintCode=outstandingTransaction, hintCode=noClient"
    )
    RFA2 = MesssageDetail(
        "Du har inte BankID-appen installerad. Kontakta din bank.",
        "The BankID app is not installed. Please contact your bank.",
        help_text="The BankID app is not installed in the mobile device."
    )
    RFA3 = MesssageDetail(
        "Åtgärden avbruten. Försök igen",
        "Action cancelled. Please try again.",
        help_text="errorCode=cancelled"
    )
    RFA4 = MesssageDetail(
        "En identifiering eller underskrift för det här personnumret är redan påbörjad. Försök igen.",
        "An identification or signing for this personal number is already started. Please try again.",
        help_text="errorCode=alreadyInProgress"
    )
    RFA5 = MesssageDetail(
        "Internt tekniskt fel. Försök igen.",
        "Internal error. Please try again.",
        help_text="errorCode=requestTimeout, errorCode=maintenance (repeatedly), errorCode=internalError"
    )
    RFA6 = MesssageDetail(
        "Åtgärden avbruten.",
        "Action cancelled.",
        help_text="status=failed, hintCode=userCancel"
    )
    RFA8 = MesssageDetail(
        ("BankID-appen svarar inte. Kontrollera att den är startad och att du har internetanslutning. "
        "Om du inte har något giltigt BankID kan du skaffa ett hos din bank. Försök sedan igen."),
        ("The BankID app is not responding. Please check that it’s started and that you have internet access. "
        "If you don’t have a valid BankID you can get one from your bank. Try again."),
        help_text="status=failed, hintCode=expiredTransaction"
    )
    RFA9 = MesssageDetail(
        "Skriv in din säkerhetskod i BankID-appen och välj Identifiera eller Skriv under.",
        "Enter your security code in the BankID app and select Identify or Sign.",
        help_text="status=pending, hintCode=userSign"
    )
    RFA13 = MesssageDetail(
        "Försöker starta BankID-appen.",
        "Trying to start your BankID app.",
        help_text="status=pending, hintCode=outstandingTransaction"
    )
    RFA14A = MesssageDetail(
        ("Söker efter BankID, det kan ta en liten stund … Om det har gått några sekunder och inget BankID "
        "har hittats har du sannolikt inget BankID som går att använda för den aktuella "
        "identifieringen/underskriften i den här datorn. Om du har ett BankID-kort, sätt in det "
        "i kortläsaren. Om du inte har något BankID kan du skaffa ett hos din bank. Om du har ett "
        "BankID på en annan enhet kan du starta din BankID-app där."),
        ("Searching for BankID, it may take a little while … If a few seconds have passed and still no "
        "BankID has been found, you probably don’t have a BankID which can be used for this "
        "identification/signing on this computer. If you have a BankID card, please insert it into "
        "your card reader. If you don’t have a BankID you can get one from your bank. If you have a "
        "BankID on another device you can start the BankID app on that device."),
        help_text="status=pending, hintCode=started, The user accesses the service using a personal computer."
    )
    RFA14B = MesssageDetail(
        ("Söker efter BankID, det kan ta en liten stund … Om det har gått några sekunder "
        "och inget BankID har hittats har du sannolikt inget BankID som går att använda "
        "för den aktuella identifieringen/underskriften i den här enheten. Om du inte "
        "har något BankID kan du skaffa ett hos din bank. Om du har ett BankID på en annan "
        "enhet kan du starta din BankID-app där."),
        ("Searching for BankID, it may take a little while … If a few seconds have passed "
        "and still no BankID has been found, you probably don’t have a BankID which can be "
        "used for this identification/signing on this device. If you don’t have a BankID you "
        "can get one from your bank. If you have a BankID on another device you can start the "
        "BankID app on that device."),
        help_text = "status=pending, hintCode=started, The user accesses the service using a mobile device."
    )
    RFA15A = MesssageDetail(
        ("Söker efter BankID, det kan ta en liten stund … Om det har gått några sekunder och "
        "inget BankID har hittats har du sannolikt inget BankID som går att använda för den aktuella "
        "identifieringen/underskriften i den här datorn. Om du har ett BankID-kort, sätt in det i kortläsaren. "
        "Om du inte har något BankID kan du skaffa ett hos din bank."),
        ("Searching for BankID:s, it may take a little while … If a few seconds have passed and still "
        "no BankID has been found, you probably don’t have a BankID which can be used for this "
        "identification/signing on this computer. If you have a BankID card, please insert it into "
        "your card reader. If you don’t have a BankID you can get one from your bank."),
        help_text = "status=pending, hintCode=started, The user accesses the service using a personal computer."
    )
    RFA15B = MesssageDetail(
        ("Söker efter BankID, det kan ta en liten stund … Om det har gått några sekunder och "
        "inget BankID har hittats har du sannolikt inget BankID som går att använda för den aktuella "
        "identifieringen/underskriften i den här enheten. Om du inte har något BankID kan du skaffa "
        "ett hos din bank."),
        ("Searching for BankID, it may take a little while … If a few seconds have passed and "
        "still no BankID has been found, you probably don’t have a BankID which can be used for "
        "this identification/signing on this device. If you don’t have a BankID you can get one "
        "from your bank."),
        help_text="status=pending, hintCode=started, The user accesses the service using a mobile device."
    )
    RFA16 = MesssageDetail(
        ("Det BankID du försöker använda är för gammalt eller spärrat. "
        "Använd ett annat BankID eller skaffa ett nytt hos din bank."),
        ("The BankID you are trying to use is blocked or too old. "
        "Please use another BankID or get a new one from your bank."),
        help_text="status=failed, hintCode=certificateErr"
    )
    RFA17A = MesssageDetail(
        ("BankID-appen verkar inte finnas i din dator eller mobil. "
        "Installera den och skaffa ett BankID hos din bank. Installera appen från din "
        "appbutik eller https://install.bankid.com"),
        ("The BankID app couldn’t be found on your computer or mobile device. "
        "Please install it and get a BankID from your bank. Install the app from your "
        "app store or https://install.bankid.com"),
        help_text="status=failed, hintCode=startFailed, RP does not use QR code."
    )
    RFA17B = MesssageDetail(
        ("Misslyckades att läsa av QR-koden. Starta BankID-appen och läs av QR-koden. "
        "Kontrollera att BankID-appen är uppdaterad. Om du inte har BankID-appen måste "
        "du installera den och skaffa ett BankID hos din bank. Installera appen från "
        "din appbutik eller https://install.bankid.com"),
        ("Failed to scan the QR code. Start the BankID app and scan the QR code. "
        "Check that the BankID app is up to date. If you don't have the BankID app, "
        "you need to install it and get a BankID from your bank. Install the app "
        "from your app store or https://install.bankid.com"),
        help_text="status=failed, hintCode=startFailed, RP uses QR code"
    )
    RFA18 = MesssageDetail(
        "Starta BankID-appen.", "Start the BankID app.",
        help_text="The name of the link or button used to start the BankID app."
    )
    RFA19 = MesssageDetail(
        "Vill du identifiera dig eller skriva under med BankID på den här datorn eller med ett Mobilt BankID?",
        "Would you like to identify yourself or sign with a BankID on this computer, or with a Mobile BankID?",
        help_text="The user accesses the service using a browser on a personal computer."
    )
    RFA20 = MesssageDetail(
        ("Vill du identifiera dig eller skriva under med ett BankID på den här enheten "
        "eller med ett BankID på en annan enhet?"),
        ("Do you want to identify yourself or sign with a BankID on this device or with "
        "a BankID on another device?"),
        help_text="The user accesses the service using a browser on a mobile device."
    )
    RFA21 = MesssageDetail(
        "Identifiering eller underskrift pågår.", 
        "Identification or signing in progress.",
        help_text="status=pending, The hintCode is unknown to RP."
    )
    RFA22 = MesssageDetail(
        "Okänt fel. Försök igen.", 
        "Unknown error. Please try again.",
        help_text="status=failed, The hintCode is unknown to RP. An error occured. The errorCode is unknown to RP."
    )
    RFA23 = MesssageDetail(
        "Fotografera och läs av din ID-handling med BankID-appen.",
        "Process your machine-readable travel document using the BankID app.",
        help_text="status=pending, hintCode=userMrtd"
    )


class UseTypeMessage():
    def __init__(self, qrcode: MesssageDetail, onfile: MesssageDetail=None) -> None:
        self.qrcode = qrcode
        self.onfile = onfile or qrcode
    
    def _compile(self, value):
        if not isinstance(value, MesssageDetail):
            try:
                value = MesssageDetail(value[0], value[1])
            except:
                value = MesssageDetail(str(value), str(value))

        return value.json()
        

    def json(self):
        return {
            UseTypes.QRCODE: self._compile(self.qrcode),
            UseTypes.ONFILE: self._compile(self.onfile),
        }


class DeviceTypeMessage():
    def __init__(self, pc, mobile) -> None:
        self.pc = pc
        self.mobile = mobile


def get_bankid_collect_message(
        status: str, hint_code: str, is_mobile: bool=True, messages: Messages=Messages
    ):
    BMS = messages
    map = {
        CollectStatuses.pending: {
            "outstandingTransaction": UseTypeMessage(BMS.RFA1, BMS.RFA13),
            "noClient": BMS.RFA1,
            "userSign": BMS.RFA9,
            "started": DeviceTypeMessage(BMS.RFA14A, BMS.RFA14B),
            "userMrtd": BMS.RFA23,
            "default": BMS.RFA21,
        },
        CollectStatuses.failed: {
            "userCancel": BMS.RFA6,
            "expiredTransaction": BMS.RFA8,
            "certificateErr": BMS.RFA16,
            "startFailed": UseTypeMessage(BMS.RFA17B, BMS.RFA17A),
            "default": BMS.RFA22
        },
    }

    try: 
        msg = map[status][hint_code]
    except KeyError:
        return {}
    
    if isinstance(msg, DeviceTypeMessage):
        msg = msg.mobile if is_mobile else msg.pc
    
    if not isinstance(msg, UseTypeMessage):
        msg = UseTypeMessage(msg)
    
    return msg.json()
