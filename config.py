import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

# fetch variables
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

DATABASE_URL = os.getenv("DATABASE_URL")