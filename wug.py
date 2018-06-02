import discord
import asyncio
import datetime
import urllib.request as u
from bs4 import BeautifulSoup
import re
import discord.utils
import os

client = discord.Client()

WUG_EMOJIS = ['🦅', '🐺', '🐯', '🦁', '🐊', '🦈', '🐻', '👐🏻']
WUG_NAMES = ['Miyu', 'Nanamin', 'Minami', 'Mayu', 'Kaya', 'Ai', 'Yoppi', 'WUG']
CONFIRMATION = ['✔', '✖']

def generate_embed(title="", description="", url="", icon="", thumbnail="", timestamp="default", footer=""):
    if timestamp == "default":
        timestamp = datetime.datetime.now()
    embed = discord.Embed(
        title=title,
        description=description,
        url=url,
        timestamp=timestamp,
    ).set_footer(text=footer, icon_url=icon).set_thumbnail(url=thumbnail)
    return embed

async def upds():
    await client.wait_until_ready()
    # ameblo
    ameblo = ""
    while not client.is_closed:
        req = u.urlopen("https://ameblo.jp/wakeupgirls")
        cont = req.read().decode('utf-8')
        soup = BeautifulSoup(cont, 'html.parser')
        title = soup.find_all(rel='bookmark')[0].get_text()
        if ameblo != title:
            thumb = ("", soup.img['src'].replace("?caw=800", ""))[soup.img['src'].startswith('https://stat.ameba.jp/user_images/')]
            icon = "https://stat.profile.ameba.jp/profile_images/20161213/12/9c/wU/p/o015001501481598004183.png"
            url = "https://ameblo.jp" + soup.find_all(rel='bookmark')[0].get('href')
            msg = soup.find_all(id='entryBody')[0].p.get_text().replace("`", "\`")

            date = soup.time['datetime']
            year, month, day = re.findall('(\d+)', date)
            date_f = datetime.date(int(year), int(month), int(day))

            time = soup.time.get_text().replace(date,"").replace("NEW! ","")
            hour, min, sec = re.findall('(\d+)', time)
            time_f = datetime.time(int(hour), int(min), int(sec))

            dt = datetime.datetime.combine(date_f, time_f)
            dt_f = dt.strftime("%A, %B %d, %Y at %I:%M:%S %p")

            e = generate_embed(title, msg, url, icon, thumb, "default", dt_f)
            await client.send_message(discord.Object(id='449125060033249280'), embed=e)
            ameblo = title
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name="Nanamin"))

@client.event
async def on_reaction_add(reaction, user):
    if user.id == client.user.id or not reaction.message.channel.id == '449810011351285771': return
    role_name = str(WUG_NAMES[WUG_EMOJIS.index(reaction.emoji)])
    role = discord.utils.get(reaction.message.server.roles, name=role_name)
    await client.add_roles(user, role)

@client.event
async def on_reaction_remove(reaction, user):
    if user.id == client.user.id or not reaction.message.channel.id == '449810011351285771': return
    role_name = str(WUG_NAMES[WUG_EMOJIS.index(reaction.emoji)])
    role = discord.utils.get(reaction.message.server.roles, name=role_name)
    await client.remove_roles(user, role)

@client.event
async def on_message(message):
    if message.author == client.user: return

    elif message.content.startswith("!roles"):
        msg = await client.send_message(message.channel, "```Loading```")
        for x in WUG_EMOJIS:
            await client.add_reaction(msg, x)
        o = ""
        for x in range(0, len(WUG_NAMES)):
            o += "{} - {}\n".format(WUG_NAMES[x], WUG_EMOJIS[x])
        await client.edit_message(msg, "```{}```".format(o))

    elif message.content.startswith("!x"):
        role_list = []
        for k in message.server.roles:
            if k.name in ('@everyone', 'Admin'): continue #don't print this role
            role_list.append(k.name)
        await client.send_message(message.channel, "\n".join(role_list))

client.loop.create_task(upds())
client.run(os.environ.get('BOT_TOKEN'))
