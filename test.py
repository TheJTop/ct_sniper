from utils import JupiterClient

jupiter = JupiterClient()

# Example: Get just a quote
'''quote = jupiter.get_quote(
    jupiter.TOKEN_ADDRESSES['SOL'],
    jupiter.TOKEN_ADDRESSES['USDC'],
    "1000000000"  # 5 SOL
)'''


# execute a full swap
result = jupiter.execute_swap(
    jupiter.TOKEN_ADDRESSES['SOL'],
    jupiter.TOKEN_ADDRESSES['USDC'],
    "10000000"  # 0.01 SOL
)