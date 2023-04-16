#!/usr/bin/env python3
import os
import time
import random
import discord # https://discordpy.readthedocs.io/
from discord import app_commands
from datetime import datetime as dt
from dotenv import load_dotenv
import lib_atomicdex as atomicdex
import lib_faucet
import lib_urls as urls
import lib_sqlite as db
import const

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

faucet = lib_faucet.Faucet(os.getenv('ATOMICDEX_IP'), os.getenv('ATOMICDEX_PORT'), os.getenv('ATOMICDEX_USERPASS'))

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

# @tree.command(name = "commandname", description = "My first application Command", guild=discord.Object(id=12417128931))
# #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.

@tree.command(name='fluxbot-help', description='Details for Flux Bot Faucet & AtomicDEX commands')
async def faucet_help(ctx):
    response = f"```\n"
    response += f"=========================== Flux Bot Commands ===========================\n"
    response += f"/atomicdex-orderbook <base> <rel>  - Details for AtomicDEX commands\n"
    response += f"/faucet-balances                   - Shows faucet balances\n"
    response += f"/faucet-drip <coin> <address>      - Sends funds from the faucet\n"
    response += f"/faucet-orders                     - Shows maker orders for faucet\n"
    response += f"/faucet-recent                     - Shows faucet funds distributed in the last 24 hours\n"
    response += f"/faucet-swaps-active               - Shows active swaps for faucet\n"
    response += f"/faucet-swaps-recent               - Shows recent swaps for faucet\n"
    response += f"```"
    await ctx.response.channel.send_message(response)


@tree.command(name='faucet-drip', description='Sends funds from the faucet')
async def faucet_drip(ctx, coin: str, address: str):
    if coin not in const.get_faucet_coins():
        await ctx.response.send_message(f"Coin `{coin}` is not supported by this faucet", delete_after=60, ephemeral=True)
    else:
        amount = str(random.randint(1, 1000)/200)
        txid = faucet.drip(coin, address, amount)
        if "error" in txid:
            await ctx.response.send_message(txid["error"])
        else:
            explorer_url = urls.get_explorer_url(coin, txid=txid['tx_hash'])
            response = f"`Sent {amount} {coin} to {address}`"
            if explorer_url:
                response += f" Link: <{explorer_url}>"
            else:
                response += f" Txid: <{txid['tx_hash']}>"
            values = (coin, address, amount, txid['tx_hash'], explorer_url, int(time.time()))
            db.update_faucet_db(values)
            await ctx.response.send_message(response, delete_after=3600)


@tree.command(name='faucet-recent', description='Shows faucet funds distributed in the last 24 hours')
async def faucet_recent(ctx):
    drips = db.recent_drips()
    sum_drips = {}
    for coin in const.get_faucet_coins():
        sum_drips.update({coin: 0})
    for drip in drips:
        print(drip)
        coin = drip[1]
        amount = drip[3]
        sum_drips[coin] += float(amount)
    response = f"```=== Recent faucet transactions ===\n"
    for coin in sum_drips:
        line = '{:>16}  {:<16}'.format(coin, sum_drips[coin])
        response += f"{line}\n"
    response += f"```"
    await ctx.response.send_message(response, delete_after=60, ephemeral=True)


@tree.command(name='faucet-balances', description='Get the faucet balance for a coin')
async def faucet_balances(ctx):
    balances = faucet.get_balances()
    response = ""
    for i in balances:
        print(i)
        if "error" in i:
            response=f"Error: {i['error']}"
        else:
            coin = i["coin"]
            balance = i["balance"]
            address = i["address"]
            response += f"`{address}`: {balance} {coin}\n"
    await ctx.response.send_message(response, delete_after=60, ephemeral=True)


@tree.command(name='faucet-orders', description='Get the orders placed by the faucet node')
async def faucet_orders(ctx):
    orders = faucet.get_my_orders()
    if not "error" in orders:
        results = orders["result"]
        rows = f"```\n| {'UUID'.center(40)} | {'PAIR'.center(20)} | {'PRICE'.center(12)} | {'MAX VOLUME'.center(12)} |\n"
        rows += f"| {'-'*40} | {'-'*20} | {'-'*12} | {'-'*12} |\n"
        for i in results["maker_orders"]:
            x = results["maker_orders"][i]
            pair = f"{x['base']}/{x['rel']}"
            rows += f"| {i.center(40)} | {pair.center(20)} | {x['price'].center(12)} | {x['max_base_vol'].center(12)} |\n"
        rows += "```"
        await ctx.response.send_message(rows, delete_after=60, ephemeral=True)
    else:
        await ctx.response.send_message(orders["error"], delete_after=60, ephemeral=True)


@tree.command(name='faucet-swaps-recent', description='Get the recent swaps from the faucet node')
async def faucet_swaps_recent(ctx):
    swaps = faucet.get_my_recent_swaps()
    if not "error" in swaps:
        swaps = swaps["result"]["swaps"]
        if len(swaps) > 0:
            rows = f"```\n| {'UUID'.center(40)} | {'PAIR'.center(20)} | {'Maker Amount'.center(12)} | {'Taker Amount'.center(12)} | {'Time Started'.center(12)} |\n"
            rows += f"| {'-'*40} | {'-'*20} | {'-'*12} | {'-'*12} | {'-'*12} |\n" 
            for x in swaps:
                pair = f"{x['maker_coin']}/{x['taker_coin']}"
                rows += f"| {x['uuid'].center(40)} | {pair.center(20)} | {x['maker_amount'].center(12)} | {x['taker_amount'].center(12)} | {str(x['my_info']['started_at']).center(12)} |\n"
            rows += "```"
        else:
            rows = "No swaps found"
        await ctx.response.send_message(rows, delete_after=60, ephemeral=True)
    else:
        await ctx.response.send_message(swaps["error"], delete_after=60, ephemeral=True)


@tree.command(name='faucet-swaps-active', description='Get the active swaps from the faucet node')
async def faucet_swaps_active(ctx):
    swaps = faucet.get_active_swaps()
    if not "error" in swaps:
        print(swaps)
        swaps = swaps["statuses"]
        if len(swaps) > 0:
            rows = f"```\n| {'UUID'.center(40)} | {'PAIR'.center(20)} | {'Maker Amount'.center(12)} | {'Taker Amount'.center(12)} |\n"
            rows += f"| {'-'*40} | {'-'*20} | {'-'*12} | {'-'*12} |\n"
            for i in swaps:
                x = swaps[i]
                pair = f"{x['maker_coin']}/{x['taker_coin']}"
                rows += f"| {i.center(40)} | {pair.center(20)} | {x['maker_amount'].center(12)} | {x['taker_amount'].center(12)} |\n"
            rows += "```"
        else:
            rows = "No active swaps found"
        await ctx.response.send_message(rows, delete_after=60, ephemeral=True)
    else:
        await ctx.response.send_message(swaps["error"], delete_after=60, ephemeral=True)


@tree.command(name='atomicdex-orderbook', description='Get the orderbook for a pair')
async def atomicdex_orderbook(ctx, base: str, rel: str):
    base = base.upper()
    rel = rel.upper()
    orderbook = faucet.get_orderbook(base, rel)
    if not "error" in orderbook:
        bids_response = lib_faucet.get_orderbook_rows(orderbook["bids"], rel)
        asks_response = lib_faucet.get_orderbook_rows(orderbook["asks"], base)
        response = lib_faucet.get_orderbook_headers(base, rel)
        response += lib_faucet.get_orderbook_subheaders(orderbook["asks"], orderbook["bids"])
        response += lib_faucet.get_orders_tabledata(asks_response, bids_response)
        await ctx.response.send_message(response, delete_after=300)
    else:
        await ctx.response.send_message(orderbook["error"], delete_after=60, ephemeral=True)


client.run(TOKEN)
