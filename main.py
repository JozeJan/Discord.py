import asyncio
import random
import time
import json
from discord import FFmpegPCMAudio
from dotenv import dotenv_values
from openai import OpenAI
import discord
from discord.ext import commands                    ####<--------------------------------------------NEVEM KVA SE KLE SPLOH DOGAJA JUST LEAVE IT ALONE!

dict = {}
import os

glasovi = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
customlist = {}
leaderboard = {}
playtime = {}
timemute = {}
global lisenforjoin, lisennextmessig, messiges
lisennextmessig = {}
lisenforjoin = {}
messiges = {}
global emojiseznam
emojiseznam = [
        "🥇 1st",
        "🥈 2nd",
        "🥉 3rd",
        "🚀 4th",
        "😎 5th",
        "😬 6th",
        "😟 7th",
        "🤢 8th",
        "💩 9th",
        "🗑️ 10th"
    ]


intents = discord.Intents.all()
global keys
keys = dotenv_values(".env")


# Create the bot instance with the specified command prefix and intents
client = commands.Bot(command_prefix='!', intents=intents)

# Event listener for when the bot has finished preparing
@client.event
async def on_ready():
    print(f' {client.user} (ID: {client.user.id})')
    print("work bitch garblt")
    print('------')
    global leaderboard, playtime
    with open('leaderboard.txt', 'r') as file:
        leaderboard = json.load(file)  # Load leaderboard as a dictionary
    with open('playtime.txt', 'r') as file:
        playtime = json.load(file)  # Load leaderboard as a dictionary


@client.command()
async def ponovi(ctx):
    voice_channel = ctx.author.voice.channel
    await voice_channel.connect()
    messageaudio = FFmpegPCMAudio("speech.mp3")
    ctx.voice_client.play(messageaudio)

@client.command()
async def govori(ctx, pglas):
    global globalctx, glas
    globalctx = ctx # rab bit kle
    glas = pglas
    if glas in glasovi:
        global dict
        ctxmauthor = ctx.message.author #sets it to a varible (for somereason it fails to make a dict without it.
        dict[ctxmauthor] = glas
        if ctx.author.voice is None:
            return await ctx.send("You are not connected to a voice channel")
        if ctx.author.voice is True:
            await ctx.send(f"You are already connected to a voice channel")
        else:
            global voice_channel
            voice_channel = ctx.author.voice.channel #sets the voice cahnel author to a shorter thingy so its nice!
            await voice_channel.connect()
            await ctx.send(f"Connected to voice channel: '{voice_channel}'")
    else:
        await ctx.send(f"Uporabite eden izmed teh glasov: {glasovi}")


@client.event #reading massages no matter what
async def on_message(message):
    await client.process_commands(message)
    message_content = message.content
    message_author = message.author
    message_words = set(message_content.split()) #splits the words (for detecting custom uwu) leave it for now

    donotread = ["!govori", "!ponovi"]
    if message_author in dict and not any(word in message_content for word in donotread): #al naredi voice file in predvaja al ne
        print(message_words)  # delite just for fun
        global custom

        custom = set(customlist).intersection(message_words)
        print(f'Cooking a new massage for -> {message_author} Rekel je: {message_content}')
        await tts(message_content, message_author)
        messageaudio = FFmpegPCMAudio("speech.mp3")

        globalctx.voice_client.play(messageaudio)
    if message_author.name in lisennextmessig and "!leavenote" not in message_content:
        name = lisennextmessig[message_author.name]
        lisenforjoin[name] = [message_content]
        print(f" printing lisen for join {lisenforjoin}")
        del lisennextmessig[message_author.name]

    else:
        print(f'{message_author} said: {message_content}')

async def speak(text, voice):  # dict author is needed to find in dict the voice theyuse
    client = OpenAI(api_key=keys["openai_api"])
    with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice=voice,
            input=text,
    ) as response:
        response.stream_to_file("speech.mp3")

async def tts(message_content, message_author): #dict author is needed to find in dict the voice theyuse
    client = OpenAI(api_key=keys["openai_api"])
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=dict.get(message_author),
        input=message_content,
    ) as response:
        response.stream_to_file("speech.mp3")

# @tasks.loop()
# async def anticheat(member):
#     if member.voice: POMOJE NA RABM VEČ
#         pass
#     else:
#         timemute[member.name] = None
#         anticheat.stop()

@client.command()
async def leaderboard(ctx):
    i = 0
    messig = []
    for tekmovalec in sorted(leaderboard.items(),key=lambda item:-item[1]):
        if i > 9:
            break
        messig.append(f"{emojiseznam[i]}: {tekmovalec[0]}, Minute: {tekmovalec[1]}")
        i+=1
    await ctx.send("\n".join(messig))
@client.command()
async def playtime(ctx):
    i = 0
    messig = []
    for tekmovalec in sorted(playtime.items(), key=lambda item: -item[1]):
        if i > 9:
            break
        messig.append(f"{emojiseznam[i]}: {tekmovalec[0]}, Minute: {tekmovalec[1]}")
        i += 1
    await ctx.send("\n".join(messig))


@client.event
async def on_voice_state_update(member, before, after):
    #does the leaderboard biznis
    channel_id = 1235858508059119649  # Replace this with your actual channel ID
    channel = client.get_channel(channel_id)
    user = member.name
    if after.self_mute and not before.self_mute: # Mutes
        timemute[user] = time.time()
        print(f"{user} muted")
        # anticheat.start(member)
    if before.channel is not None and after.channel is None:
        timemute[member.name] = None
    if before.self_mute and not after.self_mute: # Unmutes
        # anticheat.stop() #stops so it doesnt erorred
        end_time = time.time()
        if timemute[user]:
            elapsed_time = end_time - timemute[user]
            elepsed_time_hour = elapsed_time / 60
            rounded_time_hour = round(elepsed_time_hour, 2)
            if user not in playtime:
                playtime[user] = 0  # Initialize to 0 if it doesn't exist
            playtime[user] += rounded_time_hour
            with open("playtime.txt", "w") as file:
                json.dump(playtime, file)  # Dump leaderboard dictionary as JSON
            if user not in leaderboard or rounded_time_hour > leaderboard[user]:   #thanks to chat gbt i dont know what this works but it does
                leaderboard[user] = rounded_time_hour
                await channel.send(f"""New record from {member.mention}: {rounded_time_hour} minut. Your total muted time is {playtime[user]}""")
                with open("leaderboard.txt", "w") as file:
                    json.dump(leaderboard, file)  # Dump leaderboard dictionary as JSON
            print(f"{member.name} unmuted was muted for {rounded_time_hour}")
        else:
            await channel.send(f"HAHAHAH PA SEM TE DOBU {member.mention} BADNA! NČ GULJUFANJA PR BAJTA")
    #does the leavemesig
    if after.channel is not None and before.channel is None:
        print(f"{user} joined the channel")
        if user in lisenforjoin:
            list = lisenforjoin[user]
            voice_channel = after.channel
            print(f"waiting out {list}")
            await speak(f"Novo sporočilo za {user}: {list}", "echo")
            await asyncio.sleep(random.uniform(3, 5))
            print(f"reading out {list}")
            await voice_channel.connect()
            if not member.guild.voice_client:  # If the bot is not connected to any channel
                voice_client = await voice_channel.connect()
            else:
                voice_client = member.guild.voice_client
            yougotmail = FFmpegPCMAudio("yougotmail.wav")
            voice_client.play(yougotmail)
            while voice_client.is_playing():
                await asyncio.sleep(1)
            messageaudio = FFmpegPCMAudio("speech.mp3")
            voice_client.play(messageaudio)
            while voice_client.is_playing():
                await asyncio.sleep(1)
            await voice_client.disconnect()
            del lisenforjoin[user]

@client.command()
async def test(ctx):
    await ctx.send(lisennextmessig[ctx.author.name])


@client.command()
async def leavenote(ctx, ime):
    if ime:
        await ctx.send(f"Prepering a new message for {ime} the next message you send will be deliverd to him!")
        lisennextmessig[ctx.author.name] = ime
        lisenforjoin[ime] = ""


client.run(keys["discordapi_key"])
