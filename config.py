import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY: str = os.getenv("API_KEY")
    API_SECERET: str = os.getenv("API_SECERET")
    EXCHANGE_ID: str = "bybit"
    TICKER_SYMBOL: str = "BTC/USDT"
    
    
config = Config()