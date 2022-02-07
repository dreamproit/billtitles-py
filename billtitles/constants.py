#!/usr/bin/env python3

import os
from dotenv import load_dotenv

load_dotenv()

#POSTGRES_URL = os.getenv('POSTGRES_URL', default=f"postgresql://postgres:{POSTGRES_PASSWORD}@localhost")
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', default='postgres')
POSTGRES_USER = os.getenv('POSTGRES_USER', default='postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', default='postgres')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', default='localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', default='5432')

POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
