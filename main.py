# we import rss feed parser
import feedparser
# we import discord.py
import discord


# we create a class for the bot
class MyClient(discord.Client):
    # we create a function that will run when the bot is ready
    async def on_ready(self):
        print('Logged on as', self.user)

    # we create a function that will run when a message is sent
    async def on_message(self, message):
        # we check if the message is from the bot itself
        if message.author == self.user:
            return
        # we check if the message starts with !rss
        if message.content.startswith('!rss'):
            # we parse the rss feed
            d = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml')
            # we create an embed
            embed = discord.Embed(title="BBC News", description="The latest news from the BBC", color=0x00ff00)
            # we loop through the 5 latest entries
            for post in d.entries[:5]:
                # we add each entry to the embed
                embed.add_field(name=post.title, value=post.link, inline=False)
            # we send the embed
            await message.channel.send(embed=embed)


# we create an instance of the bot
client = MyClient()
# we run the bot with the token that is stocked in a file called token.txt
client.run(open('token.txt', 'r').read())