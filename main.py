import os
import discord
from discord.ext import commands, tasks
import feedparser
import asyncio
import json
import config

TOKEN = config.TOKEN
PREFIX = "!"
bot = commands.Bot(command_prefix=PREFIX)

feeds = {}

def load_feeds():
    if os.path.exists("feeds.json"):
        with open("feeds.json", "r") as f:
            data = json.load(f)
            for feed_url, feed_info in data.items():
                feed_info['channel'] = bot.get_channel(feed_info['channel_id'])
            return data
    return {}

def save_feeds():
    with open("feeds.json", "w") as f:
        data = {url: {"channel_id": info['channel'].id, "latest_post": info['latest_post']} for url, info in feeds.items()}
        json.dump(data, f)

@bot.command(name='checkfeeds')
async def checkfeeds(ctx):
    if not feeds:
        await ctx.send("Aucun flux n'est suivi pour le moment.")
        return

    new_entries_found = False
    for feed_url in feeds:
        new_entries = await check_feed_and_return_new_entries(feed_url)
        if new_entries:
            new_entries_found = True
            channel = feeds[feed_url]['channel']
            await ctx.send(f"{len(new_entries)} nouvel(le) entrée(s) trouvée(s) dans le flux {feed_url} pour le canal {channel.mention}.")
        else:
            await ctx.send(f"Aucune nouvelle entrée trouvée pour le flux {feed_url}.")

    if not new_entries_found:
        await ctx.send("Aucune nouvelle entrée trouvée pour tous les flux suivis.")

async def check_feed_and_return_new_entries(feed_url):
    feed = feedparser.parse(feed_url)
    latest_post = feeds[feed_url]['latest_post']

    if not latest_post:
        return []

    new_entries = []
    for entry in feed.entries:
        if entry.link == latest_post:
            break
        new_entries.append(entry)

    return new_entries



@bot.event
async def on_ready():
    global feeds
    print(f'{bot.user} est connecté à Discord!')
    feeds = load_feeds()
    await bot.wait_until_ready()
    check_rss.start()

@bot.command(name='addfeed')
async def addfeed(ctx, feed_url: str, channel_id: int):
    if feed_url in feeds:
        await ctx.send("Ce flux est déjà suivi.")
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        await ctx.send("Le canal spécifié n'existe pas.")
        return

    feeds[feed_url] = {
        'channel': channel,
        'latest_post': None
    }
    save_feeds()
    await ctx.send(f"Le flux {feed_url} a été ajouté et sera publié dans le canal {channel.mention}.")

async def check_feed(feed_url, max_messages=5):
    print(f"Vérification du flux : {feed_url}")
    feed = feedparser.parse(feed_url)
    channel = feeds[feed_url]['channel']
    latest_post = feeds[feed_url]['latest_post']

    if not latest_post:
        feeds[feed_url]['latest_post'] = feed.entries[0].link
        print(f"Aucun message vu précédemment, définir le dernier message vu sur {feed.entries[0].link}")
        return

    new_entries = []
    for entry in feed.entries:
        if entry.link == latest_post:
            break
        new_entries.append(entry)

    print(f"{len(new_entries)} nouveaux messages trouvés")
    new_entries.reverse()

    for i, entry in enumerate(new_entries):
        if i >= max_messages:
            print(f"La limite de {max_messages} messages a été atteinte")
            break
        await channel.send(f"**{entry.title}**\n{entry.link}")
        print(f"Publication du message : {entry.title} - {entry.link}")
        await asyncio.sleep(1)

    if new_entries:
        feeds[feed_url]['latest_post'] = new_entries[-1].link
        save_feeds()
        print(f"Mise à jour du dernier message vu sur {new_entries[-1].link}")

@tasks.loop(seconds=60)
async def check_rss():
    await asyncio.gather(*(check_feed(feed_url) for feed_url in feeds))

bot.run(TOKEN)
