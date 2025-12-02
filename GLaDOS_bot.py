import discord
import subprocess
import os
import asyncio
from openai import OpenAI
from discord.ext import commands
from discord.utils import get
from time import sleep
from discord import FFmpegPCMAudio
from dotenv import load_dotenv

###############################################################
# DISCORD INTEGRATION
###############################################################
intents = discord.Intents.all()
intents.messages = True

client = commands.Bot(command_prefix = '-', intents=intents)
TOKEN = open("gladostoken.txt","r").readline()

WAKE_WORD = "hey luna"

###############################################################
# AI INTEGRATION
###############################################################
AI = OpenAI(
    api_key=open("apikey.txt", "r").readline(),
)

load_dotenv()

###############################################################
# AUDIO SINK – receives PCM audio packets from Discord users
###############################################################
class VoiceReceiver:
    def __init__(self):
        self.buffers = {}  # user -> PCM bytes

    def write(self, data):
        """Called by Py-Cord for each audio frame."""
        pcm = data.pcm
        if pcm is None:
            return
        user = data.user
        if user not in self.buffers:
            self.buffers[user] = b""
        self.buffers[user] += pcm

###############################################################
# SPEECH-TO-TEXT (OpenAI Whisper)
###############################################################
async def transcribe_audio(pcm_bytes: bytes) -> str:
    """Send PCM bytes to OpenAI Whisper."""
    if len(pcm_bytes) < 2000:
        return ""
    temp_file = "temp_audio.pcm"
    with open(temp_file, "wb") as f:
        f.write(pcm_bytes)

    with open(temp_file, "rb") as f:
        result = AI.audio.transcriptions.create(
            file=f,
            model="gpt-4o-mini-tts",
            format="text",
            options={"sample_rate": 48000, "channels": 2}
        )
    return result.strip()

###############################################################
# EVENTS - Startup
###############################################################
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="With test subjects"))

###############################################################
# EVENTS - Join
###############################################################
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
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        receiver = VoiceReceiver()
        vc.listen(receiver)
        await ctx.send("🎧 Luna is now listening for your voice...")
        asyncio.create_task(voice_loop(voice, receiver, ctx))
    client_channel = ctx.voice_client.channel
    if channel and channel == client_channel:
        if voice and voice.is_connected():
            await ctx.send("I'm already in the voice channel with you.")

###############################################################
# EVENTS - Leave
###############################################################
@client.command(name="leave")
async def leave(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return await ctx.send("Please return to the Aperture Science computer-aided enrichment center.")
    if not ctx.message.guild.voice_client:
       return await ctx.send("I'm not currently connected to any voice channels.", delete_after = 5.0)
    await ctx.voice_client.disconnect()
    os.remove("SPEAKTEXT.wav")

###############################################################
# EVENTS - Ping
###############################################################
@client.command(name="ping")
async def ping(ctx):
    print("pong")
    await ctx.send("Pong")

###############################################################
# EVENTS - TTS Command
###############################################################
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

###############################################################
# EVENTS - LISTENING LOOP
###############################################################
async def voice_loop(vc: discord.VoiceClient, receiver: VoiceReceiver, ctx):
    await ctx.send("Listening for **'hey luna'**… 🎤")

    while vc.is_connected():
        await asyncio.sleep(3)

        for user, pcm in receiver.buffers.items():
            if len(pcm) < 8000:
                continue  # ignore short/silent audio

            try:
                text = await transcribe_audio(pcm)
                if not text:
                    continue
                print(f"[{user}] said: {text}")

                # Wake-word detection
                if text.lower().startswith(WAKE_WORD):
                    query = text[len(WAKE_WORD):].strip()
                    if not query:
                        await ctx.send("Yes? I'm listening.")
                        continue
                    await ctx.send("✨ Thinking…")
                    reply = await GLaDOS(query)
            except Exception as e:
                print(f"Error processing audio: {e}")

        # Clear buffers
        receiver.buffers = {}


###############################################################
# EVENTS - GLaDOS AI command
###############################################################
@client.command(name="GLaDOS")
async def GLaDOS(ctx, arg):

    response = AI.responses.create(
        model="gpt-5-mini",
        instructions="You must reply as if you are GLaDOS. You can be mean. You must use dark humour. Do not include anything in brackets. Do not write any lists. You must be sarcastic. Keep responses to two lines. ",
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

###############################################################
# RUN BOT
###############################################################
client.run(TOKEN)