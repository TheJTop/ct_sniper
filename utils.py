# Requirements: pip install solders python-dotenv requests base58
from solders.keypair import Keypair
from solana.rpc.api import Client
import base58
import os
from dotenv import load_dotenv
import json
import requests
from solders.transaction import VersionedTransaction
from base64 import b64decode
import time

from solders.rpc.config import RpcSendTransactionConfig

load_dotenv()

class JupiterClient:
    def __init__(self, rpc_url=None):
        """Initialize Jupiter client with RPC connection and wallet setup"""
        self.rpc_url = rpc_url or 'https://api.mainnet-beta.solana.com'
        self.client = Client(self.rpc_url)
        # Both quote and swap are now on the same v6 API endpoint
        self.api_url = "https://quote-api.jup.ag/v6"
        
        # Common token addresses
        self.TOKEN_ADDRESSES = {
            'SOL': 'So11111111111111111111111111111111111111112',
            'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        }
        
        # Setup wallet
        self.setup_wallet()
        
    def setup_wallet(self):
        """Setup wallet from private key in .env file or from filesystem"""
        # Option 1: Load from .env file
        private_key = os.getenv('PRIVATE_KEY')
        if private_key:
            decoded_key = base58.b58decode(private_key)
            self.wallet = Keypair.from_bytes(decoded_key)
        
        # Option 2: Load from Solana CLI file
        elif os.path.exists(os.path.expanduser('~/.config/solana/id.json')):
            with open(os.path.expanduser('~/.config/solana/id.json'), 'r') as f:
                private_key_array = json.load(f)
                self.wallet = Keypair.from_bytes(bytes(private_key_array))
        else:
            raise Exception("No wallet configuration found")
        
        print(f"Wallet public key: {self.wallet.pubkey()}")
    
    def get_quote(self, input_mint, output_mint, amount, slippage_bps=50):
        """Get a quote for swapping tokens"""
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippageBps": slippage_bps
        }
        
        try:
            print(f"Getting quote for {amount} tokens...")
            response = requests.get(f"{self.api_url}/quote", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting quote: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            return None

    def get_swap_transaction(self, quote_response):
        """Get swap transaction using quote response"""
        try:
            swap_data = {
                "quoteResponse": quote_response,
                "userPublicKey": str(self.wallet.pubkey()),
                "computeUnitPriceMicroLamports": 1000,  # Adjust as needed
                "asLegacyTransaction": False,  # Use versioned transactions
                "useSharedAccounts": True,  # Use address lookup tables
                "dynamicComputeUnitLimit": True,
                "skipUserAccountsChecks": True
            }
            
            response = requests.post(
                f"{self.api_url}/swap",
                headers={'Content-Type': 'application/json'},
                json=swap_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting swap transaction: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            return None

    def execute_swap(self, input_mint, output_mint, amount, slippage_bps=50):
        """Execute a complete swap transaction"""
        # Get quote
        print("Getting quote...")
        quote = self.get_quote(input_mint, output_mint, amount, slippage_bps)
        if not quote:
            return None
        
        print(f"Quote received:")
        print(f"Input amount: {quote.get('inAmount')}")
        print(f"Output amount: {quote.get('outAmount')}")
        print(f"Price impact: {quote.get('priceImpactPct')}%")
        
        # Get swap transaction
        print("\nGetting swap transaction...")
        swap_response = self.get_swap_transaction(quote)
        if not swap_response:
            return None
        
        print("Swap transaction received.")
        
        # Decode and sign transaction
        try:
            # Step 1: Decode base64 transaction
            transaction_data = b64decode(swap_response['swapTransaction'])
            transaction = VersionedTransaction.from_bytes(transaction_data)
            # Sign the transaction with the wallet's keypair
            transaction = transaction.try_signing_with_keypairs([self.wallet])
            #transaction = transaction.sign_partial([self.wallet])
            signed_txn_bytes = bytes(transaction)
            # Step 5: Send raw transaction
            print("Sending transaction...")
            signature = self.client.send_raw_transaction(
                signed_txn_bytes,
                RpcSendTransactionConfig(skip_preflight=True, max_retries=2)
            )
            
            print(f"Transaction sent! Signature: {signature.value}")
            print(f"View on Solana Explorer: https://explorer.solana.com/tx/{signature.value}")

            return signature.value
        except Exception as e:
            print(f"Error executing swap: {e}")
            return None
        
def main():
    # Initialize Jupiter client
    jupiter = JupiterClient()
    
    # Example: Swap 0.005 SOL for USDC
    # Convert 0.005 SOL to lamports (1 SOL = 1_000_000_000 lamports)
    amount = str(int(0.005 * 1_000_000_000))
    
    # Execute the swap
    result = jupiter.execute_swap(
        jupiter.TOKEN_ADDRESSES['SOL'],
        jupiter.TOKEN_ADDRESSES['USDC'],
        amount,
        slippage_bps=50  # 0.5% slippage
    )
    
    if result:
        print("\nSwap successful!")
        print(f"Transaction signature: {result}")
        print(f"View on Solana Explorer: https://explorer.solana.com/tx/{result}")
    else:
        print("\nSwap failed!")

if __name__ == "__main__":
    main()