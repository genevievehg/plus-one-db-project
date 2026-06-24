import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

def get_connection():
    return psycopg2.connect(dbname='nc_plus_one')

