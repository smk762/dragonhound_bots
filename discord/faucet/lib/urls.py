#!/usr/bin/env python3
import requests

EXPLORERS = requests.get("https://stats.kmd.io/api/info/explorers/").json()

def get_explorer_url(coin, address=None, txid=None, endpoint=None):
    if coin in EXPLORERS["results"]:
        explorer = EXPLORERS["results"][coin][0]
        if not endpoint:
            endpoint = "tx"
        return f"{explorer}{endpoint}/{txid}"
    else:
        return None

def activation_params_url():
    return "http://stats.kmd.io/api/atomicdex/coin_activation_commands/"
