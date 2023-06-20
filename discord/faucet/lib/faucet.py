#!/usr/bin/env python3
import os
import json
import requests
import random
from dotenv import load_dotenv, find_dotenv
import lib.sqlite as db
import lib.urls as urls
import lib.const as const

load_dotenv(find_dotenv())

ACTIVATION_PARAMS = requests.get(urls.activation_params_url()).json()

class Faucet():
    def __init__(self, atomicdex_ip, atomicdex_port, atomicdex_userpass):
        self.atomicdex_ip = f"{atomicdex_ip}:{atomicdex_port}"
        self.atomicdex_userpass = atomicdex_userpass
        self.faucet_coins = {}
        self.cancel_all_orders()

        # Activates coins if not already active.
        self.activate_faucet_coins()

        # Creates database table if not existing.
        db.create_tbl()


    def rpc(self, params):
        '''Sends a request to the AtomicDEX API.'''
        try:
            params.update({"userpass": self.atomicdex_userpass})
            r = requests.post(self.atomicdex_ip, json.dumps(params))
            resp = r.json()
        except requests.exceptions.RequestException as e:
            resp = {"error": f"RequestException: {e}"}
        return resp


    def get_balance(self, coin):
        params = {"method": "my_balance", "coin": coin}
        return self.rpc(params)


    def withdraw(self, coin, address, amount):
        params = {
            "mmrpc": "2.0",
            "method": "withdraw",
            "params": {
                "coin": coin,
                "to": address,
                "amount": amount
            },
            "id": 0
        }
        return self.rpc(params)


    def send_raw_tx(self, coin, tx_hex):
        params = {
            "method": "send_raw_transaction",
            "coin": coin,
            "tx_hex": tx_hex
        }
        return self.rpc(params)


    def validateaddress(self, coin, address):
        params = {
            "method": "validateaddress",
            "coin": coin,
            "address": address
        }
        return self.rpc(params)


    def get_version(self):
        params = {"method": "version"}
        return self.rpc(params)


    def stop_atomicdex(self):
        params = {"method": "stop"}
        return self.rpc(params)


    def get_my_orders(self):
        params = {"method": "my_orders"}
        return self.rpc(params)


    def get_my_recent_swaps(self):
        params = {"method": "my_recent_swaps"}
        return self.rpc(params)


    def get_my_tx_history(self):
        params = {"method": "my_tx_history"}
        return self.rpc(params)


    def get_active_orders(self):
        params = {"method": "active_orders"}
        return self.rpc(params)


    def get_active_swaps(self):
        params = {"method": "active_swaps", "include_status": True}
        return self.rpc(params)


    def get_orderbook(self, base, rel):
        params = {"method": "orderbook", "base": base, "rel": rel}
        return self.rpc(params)


    def cancel_order(self, uuid):
        params = {"method": "cancel_order", "uuid": uuid}
        return self.rpc(params)


    def cancel_all_orders(self):
        params = {
            "method": "cancel_all_orders",
            "cancel_by": {"type": "All"}
        }
        return self.rpc(params)


    def disable_coin(self, coin):
        params = {"method": "disable_coin", "coin": coin}
        return self.rpc(params)


    def setprice(self, base, rel, price, volume):
        params = {"method": "setprice", "base": base,
                  "rel": rel, "price": price, "volume": volume}
        return self.rpc(params)


    ######## Extended Methods ########
    def activate_coin(self, coin):
        if coin in ACTIVATION_PARAMS:
            params = ACTIVATION_PARAMS[coin]
            return self.rpc(params)
        else:
            return None


    def get_balances(self):
        balances = []
        for coin in const.get_faucet_coins():
            balance = self.get_balance(coin)
            balances.append(balance)
        return balances


    def update_testcoin_orders(self):
        responses = []
        faucet_coins = const.get_faucet_coins()
        print(faucet_coins)
        for base in faucet_coins:
            for rel in faucet_coins:
                if base != rel:
                    price = 1.2
                    volume = 1
                    response = self.setprice(base, rel, price, volume)
                    print(response)
                    responses.append(response)
        return responses



    def activate_faucet_coins(self):
        enabled = self.get_enabled_coins()
        for coin in const.get_faucet_coins():
            if coin not in enabled:
                self.activate_coin(coin)


    def drip(self, coin, address, amount):
        validated = self.validate_drip(coin, address)
        if not "error" in validated:
            raw = self.withdraw(coin, address, amount)
            if "result" not in raw:
                return raw
            tx_hex = raw["result"]["tx_hex"]
            txid = self.send_raw_tx(coin, tx_hex)
            return txid
        else:
            return {
                "result": {
                    "coin": coin,
                    "address": address,
                    "balance": amount,
                    "message": validated["error"]
                },
                "status": "denied"
            }


    def is_address_valid(self, coin, addr):
        '''Validates an address for a given coin.'''
        try:
            if coin == "ZOMBIE":
                # Todo: Add Zombie validation
                return True
            else:
                resp = self.validateaddress(coin, addr)
            if 'result' not in resp:
                return False
            else:
                return resp['result']['is_valid']
        except:
            return True


    def validate_drip(self, coin, address):
        if not self.is_address_valid(coin, address):
            return {"error": "Invalid address."}
        elif db.is_recently_filled(coin, address):
            return {"error": "Address has been filled recently. Please try again later."}
        return {"result": "valid"}

    def get_enabled_coins(self):
        ''' Returns a list of enabled coins. '''
        enabled = self.rpc({"method": "get_enabled_coins"})
        print(enabled)
        return [i["ticker"] for i in enabled["result"]]


##### Non Class Methods #####

def get_faucet_response(coin, amount, address, txid):
    print(txid)
    explorer_url = urls.get_explorer_url(coin, address, txid)
    response = f"Sent {amount} {coin} to {address}!"

    if explorer_url:
        response += f" Link: <{explorer_url}>"
    else:
        response += f" Txid: <{txid}>"

    return response

def get_orderbook_rows(orders, coin):
    response = ""
    if len(orders) != 0:
        for order in orders:
            price = f"{float(order['price']):10.8f}"
            volume = f"{float(order['maxvolume']):10.8f} {coin}"
            response += f"{str(price).center(22)}|{volume.center(22)}\n"
            if len(response) > 1800:
                break
    return response


def get_orderbook_subheaders(asks, bids):
    subheader = "Price".center(20) + "|" + "Volume".center(22)
    if len(asks) == 0 and len(bids) == 0:
        x = "No asks"
        y = "No bids"
        response = f"{x.center(45)}{y.center(45)}\n"
    elif len(asks) == 0:
        x = "No asks"
        response = f"{x.center(45)}{subheader.center(45)}\n"
    elif len(bids) == 0:
        x = "No bids"
        response = f"{subheader.center(45)}{x.center(45)}\n"
    else:
        response = f"{subheader.center(45)}{subheader.center(45)}\n"
    return response

def get_orderbook_headers(base, rel):
    ask_header = f"{base}/{rel} ASKS"
    bids_header = f"{base}/{rel} BIDS"
    return f"```\n{ask_header.center(45)}{bids_header.center(45)}\n "


def get_orders_tabledata(asks_response, bids_response):
    rows = max(len(asks_response.splitlines()),
               len(bids_response.splitlines()))
    bids = bids_response.splitlines()
    asks = asks_response.splitlines()
    response = ""
    for i in range(rows):
        if i < len(asks):
            response += asks[i].center(45)
        else:
            response += " "*45
        if i < len(bids):
            response += bids[i].center(45)
        response += f"\n"
    response += "```"
    return response

def get_faucet():
    return Faucet(
        const.get_atomicdex_api(),
        const.get_atomicdex_port(),
        const.get_atomicdex_userpass()
    )
