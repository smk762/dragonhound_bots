#!/usr/bin/env python3
import os
import discord # https://discordpy.readthedocs.io/
from discord import app_commands
from datetime import datetime as dt
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

# @tree.command(name = "commandname", description = "My first application Command", guild=discord.Object(id=12417128931))
# #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.

@tree.command(name='drip', description='Sends funds from the faucet')
async def drip(ctx, coin: str, address: str):
    amount = random.randint(1, 1000)/200
    txid = atomicdex.send_funds(coin, address, amount)
    explorer_url = get_explorer_url(coin, txid)
    response = f"Sent {amount} {coin} to {address}! <{explorer_url}>"
    await ctx.send(response)


@bot.command(name='faucet_balance', help='Get the faucet balance for a coin')
async def faucet_balance(ctx, coin: str):
    balance = atomicdex.get_faucet_balance(coin)
    response = f"{coin} faucet balance: {balance}"
    await ctx.send(response)


client.run(TOKEN)
