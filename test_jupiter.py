from utils import JupiterClient

jupiter = JupiterClient()

# Example: Get just a quote
'''quote = jupiter.get_quote(
    jupiter.TOKEN_ADDRESSES['SOL'],
    jupiter.TOKEN_ADDRESSES['USDC'],
    "1000000000"  # 5 SOL
)'''


jupiter = JupiterClient()
jupiter.make_trade(
    jupiter.TOKEN_ADDRESSES['SOL'], 
    jupiter.TOKEN_ADDRESSES['USDC'], 
    amount=str(int(0.0005 * 1_000_000_000))
)