import requests
import base58
import base64
import json
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders import message
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed

import os
from dotenv import load_dotenv
load_dotenv()
#CONSTANTS:
WALLET_ADDRESS = '82iGxvekNMo8xca7vCCSaKHueNua2M38Aa4iJBzRC8rR'
TOKEN_ADDRESSES = {
            'SOL': 'So11111111111111111111111111111111111111112',
            'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        }
input = TOKEN_ADDRESSES['SOL']
output = TOKEN_ADDRESSES['USDC']
amount = '500000'  # 0.0005 SOL
slippage_bps = 50
QUOTE_URL = f"https://quote-api.jup.ag/v6/quote?inputMint={input}&outputMint={output}&amount={amount}&slippageBps={slippage_bps}"
SWAP_URL = "https://quote-api.jup.ag/v6/swap"
PRIVATE_KEY = Keypair.from_bytes(base58.b58decode(os.getenv('PRIVATE_KEY')))
SOLANA_RCP_URL_ENDPOINT = "https://api.mainnet-beta.solana.com"

quote_response = requests.get(QUOTE_URL).json()

payload = {
    "quoteResponse": quote_response,
    "userPublicKey": WALLET_ADDRESS, # Replace with automatic - see utils.py
    "useSharedAccounts": True,  # Use address lookup tables
    "computeUnitPriceMicroLamports": 2000,  # Adjust as needed
    "dynamicComputeUnitLimit": True,
    "skipUserAccountsChecks": True
}

#Get Swap transaction Route
swap_route = requests.post(url=SWAP_URL, json=payload).json()['swapTransaction']
client = Client(endpoint=SOLANA_RCP_URL_ENDPOINT)

#Decode and Sign the Transaction
raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(swap_route))
signature = PRIVATE_KEY.sign_message(message.to_bytes_versioned(raw_transaction.message))
signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])

opts = TxOpts(skip_preflight=True, preflight_commitment=Processed)
result = client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)

#Extract and print the transaction ID
transaction_id = json.loads(result.to_json())['result']
print(f'transaction sent: https://explorer.solana.com/tx/{transaction_id}')

#Send Signed
