import os
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
LIMIT = int(os.getenv('LIMIT'))
URL = os.getenv('URL')
