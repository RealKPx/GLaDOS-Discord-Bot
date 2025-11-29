import time
# import glados
import discord
import asyncio
import subprocess
import pydub
from discord.ext import commands,tasks
from time import sleep
from discord import FFmpegPCMAudio
from discord.utils import get

intents = discord.Intents.all()
intents.messages = True

# tts = glados.TTS()

client = commands.Bot(command_prefix = '-', intents=intents)
TOKEN = open("gladostoken.txt","r").readline()

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="With test subjects"))

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

@client.command(name="leave")
async def leave(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return await ctx.send("Please return to the Aperture Science computer-aided enrichment center.")
    if not ctx.message.guild.voice_client:
       return await ctx.send("I'm not currently connected to any voice channels.", delete_after = 5.0)
    await ctx.voice_client.disconnect()

@client.command(name="ping")
async def ping(ctx):
    print("pong")
    await ctx.send("Pong")
    
@client.command(name="gladostts")
async def gladostts(ctx, arg):
    # audio = tts.generate_speech_audio(arg)
    # time.sleep(1)
    # tts.save_wav(audio, "SPEAKTEXT.wav")
    # time.sleep(1)
    texttospeak = "-t" + arg
    Program = subprocess.run([r'speak.exe', texttospeak, "-oSPEAKTEXT.wav", "-q"])
    time.sleep(1)

    sound = pydub.AudioSegment.from_wav("SPEAKTEXT.wav")
    sound.export("SPEAKTEXT.mp3", format="mp3")

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

client.run(TOKEN)