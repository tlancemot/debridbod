# bot.py
import os
import logging, discord
from time import sleep
from discord.ext import commands
from dotenv import load_dotenv
from clients.alldebrid import AllDebrid

intents = discord.Intents.default()
intents.typing = True
intents.messages = True
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
ALLDEBRID_TOKEN = os.getenv('ALLDEBRID_TOKEN')
bot = commands.Bot(command_prefix='!', intents=intents)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')


@bot.command()
async def debrid(ctx, link):
    await ctx.send(f'Unlocking link...please wait')
    logger.info('A link has been asked to unlock')
    result = AllDebrid.unlockLink(link=link)
    if result['status'] == "success":
        formatted_result=discord.Embed(title="✅ Link Ready !", url=result['message'], description="Your link has been unlocked")
    else :
        formatted_result=discord.Embed(title="❗ Error !", description=result['message'])
    await ctx.send(embed=formatted_result)

@bot.command()
async def checkTorrentInfo(ctx, hash):

    result = AllDebrid.get_torrent_info(hash=hash)

@bot.event
async def on_message(message):
    if message.attachments:
        for file_attch in message.attachments:
            await message.channel.send(f'Downloading file {file_attch.url}...')
            await file_attch.save(file_attch.filename)
            await message.channel.send(f'Pushing file {file_attch.url}...')
            result = AllDebrid().upload_torrent(torrent_file=file_attch.filename)
            if result['status'] == "success":
                await message.channel.send(f'File successfully pushed to AllDebrid')
                for torrent_file in result['data']['files']:
                    while torrent_file['ready'] != True:
                        logger.info(f"Not in cache {torrent_file}")
                        magnet_info = AllDebrid().magnet_info(torrent_file['id'])
                        logger.info(f"Not in cache {magnet_info}")
                        while magnet_info['status'] == 'Downloading':
                            logger.info(f"Downloading ...{magnet_info['data']['magnets']['processingPerc']}")
                        sleep(25)
                    await message.channel.send(f'torrent in cache')
                    magnet_info = AllDebrid().magnet_info(torrent_file['id'])
                    if(magnet_info['status'] == 'success'):
                        for file_link in magnet_info['data']['magnets']['links']:
                            print(file_link)
                            await message.channel.send(f"[{file_link['filename']}]: {AllDebrid().unlockLink(file_link['link'])['message']}")
            else:
                await message.channel.send(result)

bot.run(TOKEN)
