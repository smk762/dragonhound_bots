import os
import sys
from dotenv import load_dotenv, find_dotenv

#load_dotenv(find_dotenv())
load_dotenv()


def get_api_port():
    ''' Returns the port for the API. '''
    API_PORT = int(os.getenv("FASTAPI_PORT"))
    if not API_PORT:
        API_PORT = 8077
    else:
        API_PORT = int(API_PORT)
    return API_PORT


def get_ssl_certs():
    ''' Returns the SSL key and cert. '''
    SSL_KEY = os.getenv("SSL_KEY")
    if SSL_KEY == "None":
        SSL_KEY = None
    SSL_CERT = os.getenv("SSL_CERT")
    if SSL_CERT == "None":
        SSL_CERT = None
    return SSL_KEY, SSL_CERT


def get_faucet_coins():
    ''' Returns a list of faucet coins. '''
    return os.getenv('FAUCET_COINS').split(" ")


def get_db_path():
    ''' Returns the path to the database. '''
    return os.getenv('DB_PATH')


def get_atomicdex_api():
    return os.getenv('ATOMICDEX_IP')


def get_atomicdex_port():
    return int(os.getenv('ATOMICDEX_PORT'))


def get_atomicdex_userpass():
    return os.getenv('ATOMICDEX_USERPASS')


def get_subdomain():
    return os.getenv('SUBDOMAIN')



DRIP_RATE_LIMIT = 60 * 60 * 4   # 4 hrs
GLOBAL_RATE_LIMIT = 200

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "get_subdomain":
            print(get_subdomain())
