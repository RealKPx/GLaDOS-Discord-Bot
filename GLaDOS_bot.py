import discord
import subprocess
import os
import random
from openai import OpenAI
from discord.ext import commands,tasks
from time import sleep
from discord import FFmpegPCMAudio
from discord.utils import get

#############################################################################
# DISCORD INTEGRATION
#############################################################################
intents = discord.Intents.all()
intents.messages = True

client = commands.Bot(command_prefix = '-', intents=intents)
TOKEN = open("gladostoken.txt","r").readline()

#############################################################################
# OPENAI INTEGRATION
#############################################################################
AI = OpenAI(
    api_key=open("apikey.txt", "r").readline(),
)

#############################################################################
# PERSONALITIES
#############################################################################
gladospersonality = "You must reply as if you are GLaDOS. You must use dark humour. Do not use any em dashes. Do not include anything in brackets. Do not write any lists. You must be sarcastic. Keep responses to two lines. Do not give real-life advice. "

additionalprompt = "Our mission is to build aperture laboratories for you. "

personalities = [
    "You must be nice",
    "Insult the user",
    "You must swear and be extra sarcastic",
    "Include a random anecdote to the current state of affairs in a foreign country",
    "Include a random anecdote about an animal",
    "Tell the user how they are badly dressed or fat",
    "Be mean",
    "Be hateful",
    ]

canIhelp = [
    ". ",
    " and give an completely incorrect answer. "
]

#############################################################################
# EVENT - STARTUP
#############################################################################
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="With test subjects"))

#############################################################################
# EVENT - JOIN COMMAND
#############################################################################
@client.command(name="join")
async def join(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return await ctx.send("Please return to the Aperture Science computer-aided enrichment center.")
    if not ctx.author.voice:
        return await ctx.send("Did you really think that would work if you weren't connected to a voice channel? Idiot...")
    channel = ctx.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        await channel.connect()
    client_channel = ctx.voice_client.channel
    if channel and channel == client_channel:
        if voice and voice.is_connected():
            await ctx.send("I'm already in the voice channel with you.")

#############################################################################
# EVENT - LEAVE COMMAND
#############################################################################
@client.command(name="leave")
async def leave(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return await ctx.send("Please return to the Aperture Science computer-aided enrichment center.")
    if not ctx.message.guild.voice_client:
       return await ctx.send("I'm not currently connected to any voice channels.", delete_after = 5.0)
    await ctx.voice_client.disconnect()
    os.remove("SPEAKTEXT.wav")

#############################################################################
# EVENT - PING COMMAND
#############################################################################
@client.command(name="ping")
async def ping(ctx):
    print("pong")
    await ctx.send("Pong")

#############################################################################
# EVENT - TTS COMMAND
#############################################################################
@client.command(name="gladostts")
async def gladostts(ctx, arg):
    texttospeak = "-t" + arg
    subprocess.run([r'speak.exe', texttospeak, "-oSPEAKTEXT.wav", "-q"])

    if isinstance(ctx.channel, discord.channel.DMChannel):
        return await ctx.send("Please return to the Aperture Science computer-aided enrichment center.")
    if not ctx.author.voice:
        return await ctx.send("Did you really think that would work if you weren't connected to a voice channel?")
    channel = ctx.author.voice.channel
    if not channel:
        return await ctx.send("Did you really think that would work if you weren't connected to a voice channel?")
    voice = get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Did you really think that would work if I wasn't connected to a voice channel?")
    if voice and voice.is_playing():
        return await ctx.send("Please wait until I am finished before using another voice channel command.")
    if voice and voice.is_connected():
        await voice.move_to(channel)
        source = FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source = 'SPEAKTEXT.wav')
        player =  voice.play(source)

#############################################################################
# EVENT - GLaDOS COMMAND
#############################################################################
@client.command(name="GLaDOS")
async def GLaDOS(ctx, arg):

    # if personalityrating == 0:
    #     personalityrating = 1
    # elif personalityrating == 9:
    #     personalityrating = 8
    # else:
    #     personalityrating + random.choice([-1, 1])
    
    personalityrating = random.randint(0,7)

    preprompt = gladospersonality + additionalprompt + personalities[personalityrating] + random.choice(canIhelp)
    
    print(personalityrating)
    print(preprompt)

    response = AI.responses.create(
        model="gpt-5-mini",
        instructions=preprompt,
        input=arg,
    )

    texttospeak = "-t" + response.output_text
    subprocess.run([r'speak.exe', texttospeak, "-oSPEAKTEXT.wav", "-q"])

    if isinstance(ctx.channel, discord.channel.DMChannel):
        return await ctx.send("Please return to the Aperture Science computer-aided enrichment center.")
    if not ctx.author.voice:
        return await ctx.send("Did you really think that would work if you weren't connected to a voice channel?")
    channel = ctx.author.voice.channel
    if not channel:
        return await ctx.send("Did you really think that would work if you weren't connected to a voice channel?")
    voice = get(client.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Did you really think that would work if I wasn't connected to a voice channel?")
    if voice and voice.is_playing():
        return await ctx.send("Please wait until I am finished before using another voice channel command.")
    if voice and voice.is_connected():
        await voice.move_to(channel)
        source = FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source = 'SPEAKTEXT.wav')
        player = voice.play(source)
        await ctx.send(response.output_text)


#############################################################################
# RUN BOT
#############################################################################
client.run(TOKEN)