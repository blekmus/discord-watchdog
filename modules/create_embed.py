import discord
from datetime import datetime


def embed_content(entry):
    if entry['primary_rating'] == 'BLUE':
        color = discord.Color.green()
    elif entry['primary_rating'] == 'RED':
        color = discord.Color.red()
    elif entry['primary_rating'] == 'YELLOW':
        color = discord.Color.orange()
    else:
        color = discord.Color.blue()

    if entry['en_readmore_link']:
        url = entry['en_readmore_link']
    elif entry['verification_url']:
        url = entry['verification_url']
    else:
        url = None

    if entry['source_name']:
        source = entry['source_name']
    else:
        source = 'Watchdog'

    embed = discord.Embed(title=entry['en_title'],
                          color=color,
                          description=entry['en_description'],
                          url=url,
                          timestamp=datetime.fromtimestamp(entry['timestamp']/1000),
                          )

    if entry['featured_image_url']:
        embed.set_image(url=entry['featured_image_url'])

    embed.set_footer(
        text=source,
        icon_url=
        "https://watchdog-public-bucket.s3.ap-southeast-1.amazonaws.com/static/meta-blue.png"
    )

    return embed
