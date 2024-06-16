import discord
from discord.ext import commands
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
import urllib.parse
import urllib.request
import re

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Definir os intents necessários para o bot
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)

# Inicializar as filas e clientes de voz
queues = {}
voice_clients = {}

# URLs e opções do YouTube
youtube_base_url = "https://www.youtube.com/"
youtube_results_url = youtube_base_url + "results?"
youtube_watch_url = youtube_base_url + "watch?v="
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

# Opções do FFmpeg
ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": '-vn -filter:a "volume=0.25"',
}


# Evento acionado quando o bot está pronto
@client.event
async def on_ready():
    print(f"{client.user} is now jamming")


# Função para tocar a próxima música na fila
async def play_next(ctx):
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        link = queues[ctx.guild.id].pop(0)
        await play(ctx, link=link)


# Comando para tocar uma música
@client.command(name="play")
async def play(ctx, *, link):
    try:
        if ctx.guild.id not in voice_clients:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        else:
            voice_client = voice_clients[ctx.guild.id]

        if youtube_base_url not in link:
            query_string = urllib.parse.urlencode({"search_query": link})
            content = urllib.request.urlopen(youtube_results_url + query_string)
            search_results = re.findall(r"/watch\?v=(.{11})", content.read().decode())
            link = youtube_watch_url + search_results[0]

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(link, download=False)
        )
        song = data["url"]
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

        voice_client.play(
            player,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                play_next(ctx), client.loop
            ),
        )
    except Exception as e:
        print(e)


# Comando para limpar a fila
@client.command(name="clear_queue")
async def clear_queue(ctx):
    if ctx.guild.id in queues:
        queues[ctx.guild.id].clear()
        await ctx.send("Queue cleared!")
    else:
        await ctx.send("There is no queue to clear")


# Comando para pausar a música atual
@client.command(name="pause")
async def pause(ctx):
    try:
        voice_clients[ctx.guild.id].pause()
    except Exception as e:
        print(e)


# Comando para retomar a música pausada
@client.command(name="resume")
async def resume(ctx):
    try:
        voice_clients[ctx.guild.id].resume()
    except Exception as e:
        print(e)


# Comando para parar a música atual e desconectar o bot
@client.command(name="stop")
async def stop(ctx):
    try:
        voice_clients[ctx.guild.id].stop()
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
    except Exception as e:
        print(e)


# Comando para adicionar uma música à fila
@client.command(name="queue")
async def queue(ctx, *, url):
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    queues[ctx.guild.id].append(url)
    await ctx.send("Added to queue!")


# Comando para pular a música atual
@client.command(name="skip")
async def skip(ctx):
    try:
        voice_clients[ctx.guild.id].stop()
        await play_next(ctx)
        await ctx.send("Skipped current track!")
    except Exception as e:
        print(e)


# Comando para tocar uma playlist
@client.command(name="playlist")
async def playlist(ctx, *, link):
    try:
        if ctx.guild.id not in voice_clients:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        else:
            voice_client = voice_clients[ctx.guild.id]

        async def download_and_play(data):
            for entry in data["entries"]:
                song = entry["url"]
                player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
                voice_client.play(
                    player,
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        play_next(ctx), client.loop
                    ),
                )
                while voice_client.is_playing():
                    await asyncio.sleep(1)

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(link, download=False)
        )

        if "entries" in data and data["entries"]:
            first_song = data["entries"].pop(0)
            song = first_song["url"]
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

            voice_client.play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    download_and_play(data), client.loop
                ),
            )
    except Exception as e:
        print(e)


# Executar o bot
client.run(TOKEN)
