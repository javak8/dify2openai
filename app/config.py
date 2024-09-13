import os
import json

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

class Config:
    API_BASE = os.getenv("API_BASE")
