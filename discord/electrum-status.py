#!/usr/bin/env python3
import os
import discord
import requests
from datetime import datetime as dt
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('ELECTRUM_STATUS_DISCORD_TOKEN')
GUILD = int(os.getenv('ELECTRUM_STATUS_GUILD'))
CHANNEL = int(os.getenv('ELECTRUM_STATUS_CHANNEL'))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

ping_ids = {
    "electrumx.nvc.ewmcx.org:50002": {
        "discord_user": "smk",
        "discord_id": "<@448777271701143562>"
    }
}

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} is connected to {guild.name} (id: {guild.id})')
    channel = client.get_channel(CHANNEL)
    try:
        msg = ""
        status_data = requests.get("https://electrum-status.dragonhound.info/api/v1/electrums_status").json()
        for i in status_data:
            if i["status"] == "Failing":
                ping_id = ""
                last_conn = "never"
                if i["electrum"] in ping_ids:
                    ping_id = ping_ids[i["electrum"]]["discord_id"]
                if i["last_connection"]:
                    last_conn = dt.fromtimestamp(i["last_connection"])
                msg += f'[{i["coin"]}] {i["electrum"]} failing! {i["response"]}. Last connection: {last_conn} UTC. {ping_id}\n'
                if len(msg) > 1800:
                    await channel.send(msg)
                    msg = ""

        if len(msg) > 0:
            await channel.send(msg)
            msg = ""

        await client.close()
    except Exception as e:
        await channel.send(f'<@448777271701143562> Check https://stats.kmd.io/atomicdex/electrum_status/ it apears to be unresponsive: {e}')
        await client.close()


client.run(TOKEN)