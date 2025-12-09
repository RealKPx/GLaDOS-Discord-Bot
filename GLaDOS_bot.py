import discord
import subprocess
import random
from gpt4all import GPT4All
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
# AI MODEL SETUP
#############################################################################
model = GPT4All("mistral-7b-openorca.gguf2.Q4_0.gguf", device="cpu")
downloadnewmodel = model.generate("Hello!")
print(downloadnewmodel)

#############################################################################
# PERSONALITIES
#############################################################################
gladospersonality = "You must reply as if you are GLaDOS. You must use dark humour. Do not use any em dashes. Do not include anything in brackets. Do not write any lists. You must be sarcastic. Keep responses to four lines. "

additionalprompt = ""

personalities = [
    "You must be angry",
    "Insult the user",
    "You must swear and be extra sarcastic",
    "Include a random anecdote to the current state of affairs in a foreign country",
    "Include a random anecdote about animals",
    "Tell the user how they are badly dressed or fat",
    "Be mean",
    "Be hateful",
    ]

canIhelp = [
    ". ",
    " and give an completely incorrect answer. "
]

#############################################################################
# EVENT - ON READY
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

#############################################################################
# EVENT - PING COMMAND
#############################################################################
@client.command(name="ping")
async def ping(ctx):
    print("pong")
    await ctx.send("Pong")

#############################################################################
# EVENT - GLADOSTTS COMMAND
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
# EVENT - GLADOS AI COMMAND
#############################################################################
@client.command(name="GLaDOS")
async def GLaDOS(ctx, arg):
    
    personalityrating = random.randint(0,7)

    preprompt = gladospersonality + additionalprompt + personalities[personalityrating] + random.choice(canIhelp) + arg
    
    print(personalityrating)
    print(preprompt)

    with model.chat_session():
        gptoutput = model.generate(preprompt)
        print(gptoutput)

    texttospeak = "-t" + gptoutput
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

#############################################################################
# RUN BOT
#############################################################################
client.run(TOKEN)