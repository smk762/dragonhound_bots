#!/usr/bin/env python3
import time
import random
import uvicorn
from typing import Optional
import logging
from logging.config import dictConfig
from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv

import const
import lib_faucet
import lib_urls as urls
import lib_sqlite as db
from config_logger import LogConfig


# Logging config
dictConfig(LogConfig().dict())
logger = logging.getLogger("atomicdex_faucet")


# Init FaucetRPC
faucet = lib_faucet.get_faucet()
faucet_coins = const.get_faucet_coins()


# Init FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
@repeat_every(seconds=60)
def ensure_orders():
    faucet.activate_faucet_coins.sh
    faucet.update_testcoin_orders()

@app.get("/")
def read_root():
    return {
        "status": "success",
        "result": "See /docs for endpoints"
    }

# FAUCET ENDPOINTS
@app.get("/faucet/{coin}/{address}")
async def drip(coin: str, address: str, request: Request):
    if coin not in faucet_coins:
        return {
            "status": "error",
            "result": {"message": f"Coin '{coin}' not recognised. Use one of {faucet_coins}."}
        }
    amount = str(random.randint(1, 1000)/200)
    txid = faucet.drip(coin, address, amount)
    if "error" in txid:
        return txid["error"]
    elif 'tx_hash' in txid:
        explorer_url = urls.get_explorer_url(coin, address=address, txid=txid['tx_hash'])
        response = lib_faucet.get_faucet_response(coin, amount, address, txid['tx_hash'])
        values = (coin, address, amount, txid['tx_hash'], explorer_url, int(time.time()))
        db.update_faucet_db(values)
        return {
            "result": {
                "coin": coin,
                "address": address,
                "balance": amount,
                "message": response
            },
            "status": "success"
        }
    else:
        print(txid)
        return txid



@app.get("/show_faucet_db")
def show_db():
    return {
        "status": "success",
        "result": {"message": db.dump_db()}
    }


@app.get("/show_db_addr/{address}")
def show_db_addr(address: str):
    return {
        "status": "success",
        "result": {"message": db.select_addr_from_db(address)}
    }


@app.get("/rm_faucet_balances")
def show_faucet_balances():
    balances = faucet.get_balances()
    return balances


@app.get("/orderbook/{base}/{rel}")
def get_orderbook(base: str, rel: str):
    return faucet.get_orderbook(base, rel)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')

    SSL_KEY, SSL_CERT = const.get_ssl_certs()
    API_PORT = const.get_api_port()

    if SSL_KEY != "" and SSL_CERT != "" and 1==0:
        uvicorn.run("serve_api:app", host="127.0.0.1", port=API_PORT, ssl_keyfile=SSL_KEY, ssl_certfile=SSL_CERT, reload=True)
    else:
        uvicorn.run("serve_api:app", host="0.0.0.0", port=API_PORT, reload=True)

