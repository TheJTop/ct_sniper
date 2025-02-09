import requests
import os
from dotenv import load_dotenv
load_dotenv()
NTFY_CODE = os.getenv('NTFY_CODE')
HANDLES = ['elonmusk', 'cloutdotme', 'pasternak', 'kanyewest', 'realDonaldTrump', 'the_jtop']
TURN_OFF = 10 #Hours
TRIGGER_WORD = '' #If we want to tweet a word and make it stop
AMOUNT = 4 #In SOL

#To Do:
# Implement a max - market-cap feature
# Implement a volume feature
# Implement scenario when multiple CAs are found
# Implement trigger word


#Set SLIPAGE equal to ~ 2x liquidity? And if price impact is 

from logic import find_new_ca
from utils.jupiter import JupiterClient

jupiter = JupiterClient()

new_ca = find_new_ca(HANDLES, 10)

if new_ca:
    print(f"New CAs found: {new_ca}")
    for ca in new_ca:
        jupiter.make_trade(jupiter.TOKEN_ADDRESSES['SOL'], ca, amount=str(int(AMOUNT * 1_000_000_000)))
        # Send to public ntfy server

        requests.post(
            f"https://ntfy.sh/{NTFY_CODE}",
            data= "TRADE MADE"
        )

else:
        requests.post(
            f"https://ntfy.sh/{NTFY_CODE}",
            data= "NO CAs Found"
        )