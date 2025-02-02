import requests
import base58
import base64
import json
import time
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders import message
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed, Confirmed
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import traceback

load_dotenv()
PRIVATE_KEY = Keypair.from_bytes(base58.b58decode(os.getenv('PRIVATE_KEY')))

class TransactionError(Exception):
    """Custom exception for transaction-related errors"""
    pass

class JupiterClient:
    def __init__(self, rpc_url=None):
        """Initialize Jupiter client with RPC connection and wallet setup"""
        self.rpc_url = rpc_url or 'https://api.mainnet-beta.solana.com'
        self.client = Client(self.rpc_url)
        self.api_url = "https://quote-api.jup.ag/v6"
        
        # Common token addresses
        self.TOKEN_ADDRESSES = {
            'SOL': 'So11111111111111111111111111111111111111112',
            'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        }
        
        self.setup_wallet()

    def setup_wallet(self):
        """Setup wallet from private key in .env file or from filesystem"""
        private_key = os.getenv('PRIVATE_KEY')
        if private_key:
            decoded_key = base58.b58decode(private_key)
            self.wallet = Keypair.from_bytes(decoded_key)
        else:
            raise Exception("No wallet configuration found")
            
        print(f"Wallet public key: {self.wallet.pubkey()}")
    
    def get_transaction_status(self, signature: str) -> Dict[str, Any]:
            """
            Get detailed transaction status
            Returns None if transaction not found
            """
            try:
                # First try getting transaction status
                status = self.client.get_signature_statuses([signature])
                if status and status.value and status.value[0]:
                    print(f"Transaction status: {status.value[0]}")
                    return {'status': status.value[0]}

                # If status not found, try getting full transaction
                tx = self.client.get_transaction(signature, commitment=Confirmed)
                if tx and tx.value:
                    return {'transaction': tx.value}
                
                return None

            except Exception as e:
                return {'error': str(e), 'traceback': traceback.format_exc()}

    def wait_for_transaction(self, signature: str, max_retries: int = 10) -> Dict[str, Any]:
        """
        Wait for transaction confirmation and return transaction details
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                print(f"\nChecking transaction status (attempt {retry_count + 1}/{max_retries})")
                
                # Get status
                status = self.client.get_signature_statuses([signature])
                
                if status and status.value and status.value[0]:
                    tx_status = status.value[0]
                    print(f"Transaction status: {tx_status}")
                    
                    # Check confirmation status using 'Confirmed' in the string representation
                    if (tx_status.confirmation_status and 
                        'Confirmed' in str(tx_status.confirmation_status)):
                        if tx_status.err:
                            print(f"However, transaction failed with error: {tx_status.err}")
                            raise TransactionError(f"Transaction failed: {tx_status.err}")
                        return {'status': tx_status}
                    else:
                        print(f"Transaction found but waiting for confirmation. Current status: {tx_status.confirmation_status}")
                else:
                    print("Transaction not found on-chain yet...")
                
            except Exception as e:
                print(f"Error checking transaction: {str(e)}")
                print("Continuing to wait for confirmation...")
            
            retry_count += 1
            if retry_count < max_retries:
                print("Waiting 5 seconds before next check...")
                time.sleep(5)
            
        raise TransactionError(f"Transaction not confirmed after {max_retries} attempts")
    
    def get_priority_fee_estimate(self) -> int:
        """
        Get current priority fee estimate from network
        Returns microLamports per compute unit
        """
        try:
            # Get recent prioritization fees
            recent_priorities = self.client.get_recent_prioritization_fees()
            if recent_priorities and recent_priorities.value:
                # Calculate 75th percentile of recent fees to be competitive
                fees = [slot.prioritization_fee for slot in recent_priorities.value]
                fees.sort()
                index = int(len(fees) * 0.75)
                return fees[index]
            return 2000  # Default fallback
        except Exception as e:
            print(f"Error getting priority fees: {e}")
            return 2000  # Default fallback


    def make_trade(self, input_token: str, output_token: str, amount: str, slippage_bps: int = 50):
        """
        Execute a trade with enhanced error handling and transaction monitoring
        """
        try:
            # 1. Get quote
            quote_url = f"{self.api_url}/quote"
            quote_params = {
                "inputMint": input_token,
                "outputMint": output_token,
                "amount": amount,
                "slippageBps": slippage_bps
            }
            
            quote_response = requests.get(quote_url, params=quote_params)
            quote_response.raise_for_status()  # Raise exception for bad HTTP status
            quote_data = quote_response.json()
            
            if not quote_data:
                raise TransactionError("Received empty quote response from Jupiter API")
            
            # Print quote details
            print(f"Quote details:")
            print(f"Input amount: {quote_data.get('inAmount', 'Not available')}")
            print(f"Output amount: {quote_data.get('outAmount', 'Not available')}")
            print(f"Price impact: {quote_data.get('priceImpactPct', 'Not available')}%")

            # 2. Prepare swap transaction
            payload = {
                "quoteResponse": quote_data,
                "userPublicKey": str(self.wallet.pubkey()),
                "useSharedAccounts": True,
                #"computeUnitPriceMicroLamports": self.get_priority_fee_estimate(),  # Dynamic priority fee - Could be expensive ...... #Dont uncomment Yet....
                "dynamicComputeUnitLimit": True,
                "skipUserAccountsChecks": True,
                "maxAccounts": True
            }

            # Get swap transaction
            print("Requesting swap transaction...")
            swap_response = requests.post(f"{self.api_url}/swap", json=payload)
            swap_response.raise_for_status()
            swap_data = swap_response.json()
            
            if not swap_data:
                raise TransactionError("Received empty swap response from Jupiter API")
            
            if 'swapTransaction' not in swap_data:
                raise TransactionError(f"No swap transaction in response. Response: {swap_data}")

            # 4. Process and sign transaction
            print("Processing transaction...")
            raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(swap_data['swapTransaction']))
            signature = PRIVATE_KEY.sign_message(message.to_bytes_versioned(raw_transaction.message))
            signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])

            # 5. Send transaction with better error handling
            print("Sending transaction...")
            opts = TxOpts(
                skip_preflight=True,
                preflight_commitment=Processed,
                max_retries=2
            )

            result = self.client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
            
            if result is None:
                raise TransactionError("Got None response when sending transaction")
            
            if not hasattr(result, 'value') or not result.value:
                raise TransactionError("Failed to get transaction signature")

            transaction_id = result.value
            print(f'Transaction sent: https://explorer.solana.com/tx/{transaction_id}')

            # 6. Wait for and verify transaction
            print("Waiting for transaction confirmation...")
            tx_details = self.wait_for_transaction(transaction_id)
            
            if tx_details is None:
                raise TransactionError("Got None response when checking transaction details")
            
            if tx_details.get('err'):
                raise TransactionError(f"Transaction failed with error: {tx_details['err']}")
            
            print("transaction confirmed")
            return transaction_id

        except requests.exceptions.RequestException as e:
            print(f"Full error response: {e.response.text if hasattr(e, 'response') else 'No response text'}")
            raise TransactionError(f"API request failed: {str(e)}")
        except Exception as e:
            raise TransactionError(f"Trade failed: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        jupiter = JupiterClient()
        jupiter.make_trade(
            jupiter.TOKEN_ADDRESSES['SOL'], 
            jupiter.TOKEN_ADDRESSES['USDC'], 
            amount=str(int(0.0005 * 1_000_000_000))
        )
    except TransactionError as e:
        print(f"Transaction failed: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")