import os
import discord
from discord.ext import commands, tasks
from timeit import default_timer as time_func
from datetime import timedelta, datetime
import logging
from modules.get_entries import get_entries
from modules.create_embed import embed_content
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix='.watchdog ')
token = os.environ['TOKEN']

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s] - %(message)s",
    filename="discord-watchdog.log",
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


bot.is_startup = True
bot.channel_name = 'watchdog'


# return formatted hh mm ss
def timematter(x):
    s = timedelta(seconds=x)

    if s.days < 1:
        if s.seconds <= 60 * 60:
            out = f'{s.seconds//60}m {s.seconds - (s.seconds//60)*60}s'
        else:
            out = f'{s.seconds//(60*60)}h {int(s.seconds/60 - (s.seconds//3600)*60)}m {s.seconds - (s.seconds//60)*60}s'
    else:
        out = f'{s.days}d {s.seconds//(60*60)}h {int(s.seconds/60 - (s.seconds//3600)*60)}m {s.seconds - (s.seconds//60)*60}s'
    return out


@bot.event
async def on_ready():
    if not bot.is_startup:
        return

    bot.run_time = time_func()
    bot.last_check = datetime.now()
    bot.is_startup = False
    check_loop.start()
    print("started")
    logging.info("Bot started")

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".watchdog help"))


@tasks.loop(minutes=30, count=None)
async def check_loop():
    logging.info('starting check_loop')

    # get channel to send messages
    for i in bot.get_guild(646638903503224833).text_channels:
        if i.name == bot.channel_name:
            channel = i

    # get current news entry
    with open('current.txt', 'r') as file:
        current_entry = int(file.readlines()[0])
        logging.info(f'current.txt id: {str(current_entry)}')

    # send requests
    news_entries = get_entries(current_entry)

    if news_entries:
        logging.info(f'recieved {len(news_entries)} new entries')

    # if there aren't any entries end loop
    if not news_entries or len(news_entries) == 0:
        bot.last_check = datetime.now()
        logging.info('no entries to process')
        logging.info('ending check_loop')
        return

    # loop through entries and send embeds
    for entry in news_entries:
        logging.info(f"sending embed for id: {str(entry['id'])}")
        embed = embed_content(entry)
        await channel.send(embed=embed)

    # set new current entry id to curret.txt
    new_current_entry = news_entries[0]['id']
    with open('current.txt', 'w') as file:
        logging.info(f"saving new current id: {str(new_current_entry)}")
        file.write(str(new_current_entry))

    # set last_check for .watchdog stats
    bot.last_check = datetime.now()
    logging.info('ending check_loop')


@bot.command()
async def stats(ctx):
    if not (ctx.channel.name == bot.channel_name):
        temp = await ctx.send('Wrong channel')
        await temp.delete(delay=5)
        await ctx.message.delete(delay=5)
        return

    # main embed
    embed = discord.Embed(
        title="**STATS**",
        colour=discord.Colour(0x3cb4b5),
        description="Status parameters of the bot"
    )

    # run time
    run_time = int(time_func() - bot.run_time)
    embed.add_field(name="__Run-time__", value=f"```{timematter(run_time)}```", inline=False)

    # last new entry id
    with open('./current.txt', 'r') as file:
        current_entry = file.readlines()[0]

    embed.add_field(name="__Last-entry-id__", value=f"```{current_entry}```", inline=False)

    # last check
    time_diff = datetime.now() - bot.last_check
    embed.add_field(name="__Last-check__", value=f"```{timematter(time_diff.seconds)}```", inline=False)

    await ctx.send(embed=embed)


bot.remove_command('help')
@bot.command(name='help')
async def help(ctx, var=None):
    if var is None:
        embed = discord.Embed(
            title='**COMMAND LIST**',
            colour=discord.Colour(0x3cb4b5),
            description="The current prefix is `.watchdog`. Try `help <command>` to get more info about individual commands."
        )
        embed.add_field(
            name="Commands",
            value="```stats```")
        await ctx.send(embed=embed)

    elif var == 'stats':
        embed = discord.Embed(
            title='**stats** (command)',
            colour=discord.Colour(0x3cb4b5),
            description="Shows the current stats of the bot."
        )
        embed.add_field(
            name="Usage",
            value="```stats```",
            inline=False
        )
        await ctx.send(embed=embed)

    else:
        raise AttributeError


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        logging.info("Bot activity. Missing arguments")
        await ctx.send("Missing arguments")
        return

    elif isinstance(error, commands.CommandInvokeError):
        logging.info("Bot activity. Syntax error")
        await ctx.send("Syntax error")
        return

    elif isinstance(error, commands.CommandNotFound):
        logging.info("Bot activity. Command not found")
        await ctx.send('Command not found')
        return

    raise error


bot.loop.run_until_complete(bot.run(token))
