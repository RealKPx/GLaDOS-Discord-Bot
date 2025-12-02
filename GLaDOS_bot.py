import discord
import subprocess
import os
import asyncio
from openai import OpenAI
from discord.ext import commands,tasks
from time import sleep
from discord import FFmpegPCMAudio
from discord.utils import get

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

###############################################################
# AUDIO SINK – receives PCM audio packets from Discord users
###############################################################
class VoiceReceiver(discord.sinks.RawDataSink):
    def __init__(self, wake_callback):
        super().__init__()
        self.buffer = b""
        self.wake_callback = wake_callback

    def raw_data(self, user, data):
        # data is PCM 48kHz 16-bit stereo
        self.buffer += data

    async def cleanup(self):
        # Fired when sink stops
        pass

###############################################################
# SPEECH-TO-TEXT (OpenAI Whisper)
###############################################################
async def transcribe_audio(pcm_bytes: bytes) -> str:
    """Send audio to OpenAI Whisper for STT."""
    with open("temp.pcm", "wb") as f:
        f.write(pcm_bytes)

    audio_file = open("temp.pcm", "rb")

    result = client_ai.audio.transcriptions.create(
        file=audio_file,
        model="gpt-4o-mini-tts",
        format="text",
        # pcm requires parameters
        options={"sample_rate": 48000, "channels": 2}
    )

    return result

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
    client_channel = ctx.voice_client.channel
    if channel and channel == client_channel:
        if voice and voice.is_connected():
            await ctx.send("I'm already in the voice channel with you.")
    
    await start_listening(vc, ctx.channel)

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
# LISTENING LOOP
###############################################################
async def start_listening(vc: discord.VoiceClient, text_channel):
    while True:
        sink = VoiceReceiver(wake_callback=None)
        vc.start_recording(
            sink,
            finished_callback=lambda *args: None
        )

        await asyncio.sleep(3)
        vc.stop_recording()

        pcm_data = sink.buffer

        if len(pcm_data) < 20000:  
            continue  # ignore silence

        # Transcribe audio
        text = await transcribe_audio(pcm_data)
        if not text:
            continue

        print("Heard:", text)

        # Wake-word detection
        if text.lower().startswith(WAKE_WORD):
            query = text[len(WAKE_WORD):].strip()
            if not query:
                await text_channel.send("Yes? I'm listening.")
                continue

            await text_channel.send("🎤 Heard you. Thinking...")
            reply = await ask_ai(query)
            await text_channel.send(reply)

###############################################################
# RUN BOT
###############################################################
client.run(TOKEN)