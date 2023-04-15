#!/usr/bin/env python3
import os
import sys
import json
import time
import random
import string
import mnemonic
from dotenv import load_dotenv

load_dotenv()

special_chars = ["@", "~", "-", "_", "|", ":", "+"]


def generate_rpc_pass(length):
    rpc_pass = ""
    quart = int(length/4)
    while len(rpc_pass) < length:
        rpc_pass += ''.join(random.sample(string.ascii_lowercase,
                            random.randint(1, quart)))
        rpc_pass += ''.join(random.sample(string.ascii_uppercase,
                            random.randint(1, quart)))
        rpc_pass += ''.join(random.sample(string.digits,
                            random.randint(1, quart)))
        rpc_pass += ''.join(random.sample(special_chars,
                            random.randint(1, quart)))
    str_list = list(rpc_pass)
    random.shuffle(str_list)
    return ''.join(str_list)


def configure_atomicdex(path=None):
    print("Configuring AtomicDEX...")
    if not path:
        path = ""
    elif not path.endswith("/"):
        path = f"{path}/"

    ATOMICDEX_IP = os.getenv("ATOMICDEX_IP")
    ATOMICDEX_PORT = os.getenv("ATOMICDEX_PORT")
    ATOMICDEX_PASS = os.getenv("ATOMICDEX_PASS")
    ATOMICDEX_SEEDPHRASE = os.getenv("ATOMICDEX_SEEDPHRASE")
    if None in [ATOMICDEX_IP, ATOMICDEX_PORT, ATOMICDEX_PASS, ATOMICDEX_SEEDPHRASE]:
        print("Missing environment variables. Please check .env file.")
        print("or run './configure.py env_vars' to populate.")
        print("Exiting...")
        sys.exit(1)

    conf = {
        "gui": "FAUCET",
        "netid": 7777,
        "rpc_ip": f"{ATOMICDEX_IP}:{ATOMICDEX_PORT}",
        "rpc_password": ATOMICDEX_PASS,
        "passphrase": ATOMICDEX_SEEDPHRASE,
        "userhome": "/${HOME#\"/\"}"
    }

    with open(f"{path}MM2.json", "w+") as f:
        json.dump(conf, f, indent=4)
    print(f"{path}MM2.json file created.")

    with open(f"{path}userpass", "w+") as f:
        f.write(f'{path}userpass="{rpc_password}"')
    print(f"{path}userpass file created.")
    print("AtomicDEX configured successfully!")

def generate_seed():
    q = "[E]nter seed manually or [G]enerate one? [E/G]: "
    a = input(q)
    while a not in ["G", "g", "E", "e"]:
        print("Invalid input!")
        a = input(q)

    if a in ["E", "e"]:
        passphrase = input("Enter a seed phrase: ")
    else:
        m = mnemonic.Mnemonic('english')
        passphrase = m.generate(strength=256)
    return passphrase


def check_dotenv():
    req_vars = ["ATOMICDEX_SEEDPHRASE", "ATOMICDEX_PASS", "ATOMICDEX_PORT", "ATOMICDEX_IP"]
    with open(".env", "r+") as f:
        existing_vars = [k.split("=")[0] for k in f.readlines()]
        print(existing_vars)
    with open(".env", "a+") as f:
        vars_to_add = [k for k in req_vars if k not in existing_vars]
        print(vars_to_add)

        if vars_to_add:
            for var in vars_to_add:
                if var == "ATOMICDEX_SEEDPHRASE":
                    val = generate_seed()
                elif var == "ATOMICDEX_PASS":
                    val = generate_rpc_pass(16)
                elif var == "ATOMICDEX_PORT":
                    val = 7783
                elif var == "ATOMICDEX_IP":
                    val = 'http://127.0.0.1'
                else:
                    val = input(f"Enter the value for {var}: ")
                f.write(f'{var}="{val}"\n')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "env_vars":
            check_dotenv()
        elif sys.argv[1] == "atomicdex":
            configure_atomicdex('atomicdex')
        else:
            print("Unknown argument")

