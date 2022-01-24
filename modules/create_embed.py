import discord
from datetime import datetime


def embed_content(entry):
    # main embed

    if entry['type'] == 'fake':
        # red hue
        color = 16739436
    else:
        # green hue
        color = 10025628

    if entry['url'].startswith('http'):
        url = entry['url']
    else:
        url = False

    embed = discord.Embed(
        title=entry['title'],
        color=discord.Color(color),
        description=entry['description'],
        url=url,
        timestamp=datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
    )

    # footer
    embed.set_footer(text=entry['source_name'], icon_url="https://watchdog.paladinanalytics.com/site_image.png")

    return embed
