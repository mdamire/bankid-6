import time
import argparse
from bankid6 import BankIdClient, CollectStatuses, UseTypes, Languages, BankIdError, HintCodes

# Create the parser
parser = argparse.ArgumentParser(description="Process some inputs.")

# Add the arguments
parser.add_argument(
    's',
    choices=['auth', 'sign', 'phone_auth', 'phone_sign'],
    default='auth',
    help='Specify the service type (default: auth)'
)
parser.add_argument(
    '-ssn',
    help='Specify the Social Security Number'
)

args = parser.parse_args()

bc = BankIdClient()
if args.s == 'auth':
    sr = bc.auth('192.168.0.1')
    print('Launch URL:', sr.launch_url())
elif args.s == 'sign':
    sr = bc.sign('192.168.0.1', 'test message')
    print('Launch URL:', sr.launch_url())
elif args.s == 'phone_auth':
    sr = bc.phone_auth(args.ssn, 'RP')
elif args.s == 'phone_sign':
    sr = bc.phone_sign(args.ssn, 'RP', 'test message')


while True:
    time.sleep(1)
    cr = bc.collect()
    print('User message: ', cr.message)
    if cr.status in [CollectStatuses.failed, CollectStatuses.complete]:
        break
