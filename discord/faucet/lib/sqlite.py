#!/usr/bin/env python3
import os
import time
import sqlite3
from dotenv import load_dotenv, find_dotenv
import lib.const as const

DB_PATH = const.get_db_path()

# Create table if not existing
def create_tbl():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='faucet';''')
        if len(cursor.fetchall()) == 0 :
            print('Table does not exist.')
            cursor.execute('''
                    CREATE TABLE faucet (
                        id INTEGER PRIMARY KEY,
                        coin text,
                        address text,
                        amount int,
                        txid text,
                        explorer_url text,
                        refill_time int
                    )
            ''')
            conn.commit()


def update_faucet_db(values):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO faucet(coin, address, amount, txid, explorer_url, refill_time) VALUES(?,?,?,?,?,?)", values)
        conn.commit()


def dump_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM faucet ORDER BY refill_time DESC LIMIT 200 ;").fetchall()
        return rows

def recent_drips(since=86400):
    with sqlite3.connect(DB_PATH) as conn:
        day_ago = str(int(time.time())-since)
        cursor = conn.cursor()
        rows = cursor.execute(f"SELECT * FROM faucet WHERE refill_time > {day_ago} ORDER BY refill_time DESC;").fetchall()
        return rows


def get_pending_tx():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM faucet WHERE status = 'pending';").fetchall()
        return rows


def select_addr_from_db(addr):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        sql = "SELECT * FROM faucet WHERE address = ?"
        rows = cursor.execute(sql, (addr,)).fetchall()
        return rows


def is_dry(coin):
    ''' Checks if global outflow exceeds rate limit '''
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        last_drip = str(int(time.time()) - const.DRIP_RATE_LIMIT)
        sql = "SELECT COUNT(*) FROM faucet WHERE coin = ? AND refill_time > "+last_drip
        count = cursor.execute(sql, (coin,)).fetchone()
        if count[0] > const.GLOBAL_RATE_LIMIT:
            return True
        return False


def is_recently_filled(coin, addr):
    ''' Checks if address recenty filled '''
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        last_drip = str(int(time.time()) - const.DRIP_RATE_LIMIT)
        sql = "SELECT * FROM faucet WHERE  coin = ? AND address = ? AND refill_time > "+last_drip
        rows = cursor.execute(sql, (coin, addr)).fetchall()
        if len(rows) > 0:
            return True
        return False


create_tbl()
