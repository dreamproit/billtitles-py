#!/usr/bin/env python3

import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_PW = os.getenv('POSTGRES_PW', default='1234')
