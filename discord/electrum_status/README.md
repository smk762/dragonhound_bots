## Install Dependencies:
- `pip3 install -r requirements.txt`


## Usage
- For alert bots, set these to run periodically via crontab. For example, to send alerts ever 4 hours, add an entry like `0 */4 * * * /home/smk/dragonhound_bots/discord/electrum-status.py`