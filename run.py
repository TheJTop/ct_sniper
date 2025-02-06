HANDLES = ['elonmusk', 'stoolpresidente', 'cloutdotme', 'pasternak', 'kanyewest', 'realDonaldTrump', 'the_jtop']
SLIPAGE = 0.2
TURN_OFF = 10 #Hours
TRIGGER_WORD = '' #If we want to tweet a word and make it stop

#To Do:
# Implement a max - market-cap feature
# Implement a volume feature
# Implement scenario when multiple CAs are found

from logic import find_new_ca
from utils import JupiterClient

jupiter = JupiterClient()


new_ca = find_new_ca(HANDLES, 10)

if new_ca:
    print(f"New CAs found: {new_ca}")
    for ca in new_ca:
        jupiter.make_trade(jupiter.TOKEN_ADDRESSES['SOL'], ca, amount=str(int(0.0005 * 1_000_000_000)))