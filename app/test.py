"""
test - 
Author: 
Date: 2024/8/30
"""

import os
import json
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

COZE_API_BASE = os.getenv("COZE_API_BASE", "api.coze.com")
DEFAULT_BOT_ID = os.getenv("BOT_ID", "")
BOT_CONFIG = json.loads(os.getenv("BOT_CONFIG", "{}"))

print(DEFAULT_BOT_ID)