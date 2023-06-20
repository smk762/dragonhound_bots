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
    "electrum.server:50000": {
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
        failing_coins = {}
        status_data = requests.get("https://electrum-status.dragonhound.info/api/v1/electrums_status").json()

        for i in status_data:
            if i["status"] == "Failing":

                last_conn = "Never"
                if i["last_connection"]:
                    last_conn = f'{dt.fromtimestamp(i["last_connection"])} UTC'

                coin = i["coin"]
                if coin not in failing_coins:
                    failing_coins.update({coin: []})

                ping = None
                if i["electrum"] in ping_ids:
                    ping = ping_ids[i["electrum"]]["discord_id"]

                msg = '{:<12}'.format(f'[{coin}]')
                msg += '{:<48}'.format(f'{i["electrum"]}')
                msg += '{:<124}'.format(f'{i["response"][:120]}')
                msg += f'Last: {last_conn}\n'

                failing_coins[coin].append({"msg": msg, "ping": ping})

        failed_coins_list = list(failing_coins.keys())
        failed_coins_list.sort()

        msg = ""
        pingums = []
        for coin in failed_coins_list:
            for i in failing_coins[coin]:
                if i["ping"]:
                    pingums.append(i["ping"])

                msg += i["msg"]
                if len(msg) > 1700:
                    msg = f"{' '.join(pingums)}\n```\n{msg}\n```"
                    await channel.send(msg)
                    msg = ""
                    pingums = []

        if msg != "":
            msg = f"{' '.join(pingums)}\n```\n{msg}\n```"
            await channel.send(msg)


        await client.close()
    except Exception as e:
        await channel.send(f'<@448777271701143562> Check <https://stats.kmd.io/atomicdex/electrum_status/> - it appears to be unresponsive: {e}')
        await client.close()


client.run(TOKEN)
