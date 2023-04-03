import discord
import feedparser
import asyncio
import pickle

from config import TOKEN

client = discord.Client()

rss_feed_url = None  # initialiser le lien RSS

CHANNEL_ID = 1234567890  # remplacer par l'ID du channel

def read_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    latest_entries = feed.entries[:5]
    results = []
    for entry in latest_entries:
        title = entry.title
        link = entry.link
        result = f"{title} - {link}"
        results.append(result)
    return results

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    global rss_feed_url
    try:
        with open("rss_feed.pkl", "rb") as f:
            rss_feed_url = pickle.load(f)  # récupérer le lien RSS à partir du fichier
    except FileNotFoundError:
        print("No RSS feed found")

async def read_rss_feed_task():
    await client.wait_until_ready()
    while not client.is_closed():
        if rss_feed_url is not None:
            results = read_rss_feed(rss_feed_url)
            for result in results:
                channel = await client.fetch_channel(CHANNEL_ID)  # récupérer le channel pour envoyer les résultats
                await channel.send(result)
        await asyncio.sleep(1200)  # attendre 20 minutes avant de relancer la tâche

@client.event
async def on_message(message):
    global rss_feed_url  # déclarer la variable rss_feed_url comme globale
    if message.content.startswith('!set_rss'):
        rss_feed_url = message.content.split(' ')[1]
        with open("rss_feed.pkl", "wb") as f:
            pickle.dump(rss_feed_url, f)  # enregistrer le lien RSS dans le fichier
        await message.channel.send(f"RSS feed set to {rss_feed_url}")
    elif message.content.startswith('!get_rss'):
        if rss_feed_url is not None:
            await message.channel.send(f"Current RSS feed is {rss_feed_url}")
        else:
            await message.channel.send("No RSS feed has been set")

client.loop.create_task(read_rss_feed_task())  # créer la tâche asynchrone pour lire le flux RSS

client.run(TOKEN)
