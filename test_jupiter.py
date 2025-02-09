from utils.jupiter import JupiterClient

jupiter = JupiterClient()

# Example: Get just a quote
'''quote = jupiter.get_quote(
    jupiter.TOKEN_ADDRESSES['SOL'],
    jupiter.TOKEN_ADDRESSES['USDC'],
    "1000000000"  # 5 SOL
)'''


# jupiter = JupiterClient()
# jupiter.make_trade(
#     jupiter.TOKEN_ADDRESSES['SOL'], 
#     jupiter.TOKEN_ADDRESSES['USDC'], 
#     amount=str(int(0.0005 * 1_000_000_000))
# )
x = jupiter.get_market_info(jupiter.TOKEN_ADDRESSES['SOL'], jupiter.TOKEN_ADDRESSES['USDC'], amount = str(int(500000 * 1_000_000_000)))



import requests
import os
from dotenv import load_dotenv

load_dotenv()
NTFY_CODE = os.getenv('NTFY_CODE')

requests.post(
    f"https://ntfy.sh/{NTFY_CODE}",
    data=x
)