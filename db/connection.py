import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

database_name = os.environ["DATABASE_NAME"]

def get_connection():
    return psycopg2.connect(dbname=database_name)

