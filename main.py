import discord
from discord.ext import commands
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
import urllib.parse
import urllib.request
import re
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import logging

# Configurar logging com mais detalhes
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("music_bot")

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configurações do bot
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)

# Estruturas de dados
queues = {}
voice_clients = {}
downloading_tasks = {}
thread_pool = ThreadPoolExecutor(max_workers=3)

# Configurações específicas para YouTube
yt_dl_options = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "extract_flat": True,  # Alterado para True para melhor suporte a playlists
    "ignoreerrors": True,
    "nocheckcertificate": True,
    "no_warnings": True,
    "quiet": True,
    "force_generic_extractor": False,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "opus",
        }
    ],
    "youtube_include_dash_manifest": False,
}

ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": '-vn -filter:a "volume=0.25"',
}


class Song:
    def __init__(self, url, title=None, duration=None, audio_url=None):
        self.url = url
        self.title = title or "Unknown Title"
        self.duration = duration
        self.audio_url = audio_url

    def __str__(self):
        return f"{self.title} ({self.duration}s)" if self.duration else self.title


class MusicQueue:
    def __init__(self):
        self.queue = deque()
        self.current = None
        self.processing = False


music_queues = {}


@client.event
async def on_ready():
    logger.info(f"{client.user} está pronto para tocar música!")


def is_youtube_playlist(url):
    """Verifica se a URL é uma playlist do YouTube"""
    return "youtube.com" in url and ("list=" in url or "playlist?list=" in url)


def extract_playlist_id(url):
    """Extrai o ID da playlist de uma URL do YouTube"""
    if "list=" in url:
        return url.split("list=")[1].split("&")[0]
    return None


async def extract_song_info(url):
    """Extrai informações da música com melhor tratamento para YouTube"""
    loop = asyncio.get_event_loop()
    try:
        logger.info(f"Extraindo informações da música: {url}")

        # Configurações específicas para extração única
        single_options = yt_dl_options.copy()
        single_options["noplaylist"] = True

        with yt_dlp.YoutubeDL(single_options) as ydl:
            try:
                data = await loop.run_in_executor(
                    None, lambda: ydl.extract_info(url, download=False)
                )

                if not data:
                    logger.error(f"Nenhum dado extraído para URL: {url}")
                    return None

                # Para URLs do YouTube, garantir que temos a URL correta
                if "youtube.com" in url or "youtu.be" in url:
                    url = f"https://www.youtube.com/watch?v={data['id']}"

                return Song(
                    url=url,
                    title=data.get("title", "Unknown Title"),
                    duration=data.get("duration"),
                    audio_url=data.get("url"),
                )
            except Exception as e:
                logger.error(f"Erro ao extrair dados com yt-dlp: {str(e)}")
                return None
    except Exception as e:
        logger.error(f"Erro ao extrair informações da música: {str(e)}")
        return None


async def process_playlist(ctx, url):
    """Processamento otimizado de playlist com melhor detecção de entradas"""
    guild_id = ctx.guild.id
    if guild_id not in music_queues:
        music_queues[guild_id] = MusicQueue()

    try:
        await ctx.send("🔍 Analisando playlist...")

        # Configurações específicas para playlist
        playlist_options = {
            "extract_flat": True,
            "quiet": True,
            "ignoreerrors": True,
            "no_warnings": True,
            "playlistend": 100,  # Limite de 100 músicas por playlist para evitar sobrecarga
        }

        with yt_dlp.YoutubeDL(playlist_options) as ydl:
            try:
                # Extrair informações da playlist
                playlist_info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(url, download=False)
                )

                if not playlist_info:
                    await ctx.send("❌ Não foi possível carregar a playlist.")
                    return

                # Verificar se é uma playlist ou vídeo único
                if "entries" in playlist_info:
                    entries = list(filter(None, playlist_info["entries"]))
                else:
                    # Se não for uma playlist, trata como vídeo único
                    entries = [playlist_info]

                if not entries:
                    await ctx.send("❌ Nenhuma música encontrada na playlist.")
                    return

                await ctx.send(f"📋 Encontradas {len(entries)} músicas!")

                # Processa primeira música imediatamente
                first_entry = entries[0]
                first_url = (
                    first_entry.get("url")
                    or f"https://www.youtube.com/watch?v={first_entry['id']}"
                )

                # Configurações para extração de música única
                single_options = yt_dl_options.copy()
                single_options["noplaylist"] = True

                with yt_dlp.YoutubeDL(single_options) as single_ydl:
                    first_song_info = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: single_ydl.extract_info(first_url, download=False)
                    )

                    if first_song_info:
                        first_song = Song(
                            url=first_url,
                            title=first_song_info.get("title", "Unknown Title"),
                            duration=first_song_info.get("duration"),
                            audio_url=first_song_info.get("url"),
                        )

                        music_queues[guild_id].queue.append(first_song)
                        await ctx.send(f"🎵 Começando com: {first_song.title}")

                        if (
                            guild_id in voice_clients
                            and not voice_clients[guild_id].is_playing()
                        ):
                            await play_next(ctx)

                # Processa resto da playlist em background
                if len(entries) > 1:
                    await ctx.send(
                        f"⏳ Carregando mais {len(entries)-1} músicas em segundo plano..."
                    )
                    asyncio.create_task(process_remaining_songs(ctx, entries[1:]))

            except Exception as e:
                logger.error(f"Erro ao extrair dados da playlist: {str(e)}")
                await ctx.send(f"❌ Erro ao processar a playlist: {str(e)}")

    except Exception as e:
        logger.error(f"Erro em process_playlist: {str(e)}")
        await ctx.send(f"❌ Ocorreu um erro: {str(e)}")


async def process_remaining_songs(ctx, entries):
    """Processamento otimizado das músicas restantes da playlist"""
    guild_id = ctx.guild.id
    processed = 0
    failed = 0

    # Configurações para extração de música única
    single_options = yt_dl_options.copy()
    single_options["noplaylist"] = True

    for entry in entries:
        try:
            if not entry:
                continue

            # Construir URL do vídeo
            video_url = (
                entry.get("url") or f"https://www.youtube.com/watch?v={entry['id']}"
            )

            with yt_dlp.YoutubeDL(single_options) as ydl:
                try:
                    info = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: ydl.extract_info(video_url, download=False)
                    )

                    if info:
                        song = Song(
                            url=video_url,
                            title=info.get("title", "Unknown Title"),
                            duration=info.get("duration"),
                            audio_url=info.get("url"),
                        )

                        music_queues[guild_id].queue.append(song)
                        processed += 1

                except Exception as e:
                    logger.error(f"Erro ao processar música individual: {str(e)}")
                    failed += 1
                    continue

        except Exception as e:
            logger.error(f"Erro ao processar entrada da playlist: {str(e)}")
            failed += 1
            continue

    await ctx.send(
        f"✅ Playlist processada!\n"
        f"✓ Músicas adicionadas: {processed}\n"
        f"✗ Falhas: {failed}"
    )


def is_youtube_playlist(url):
    """Verificação melhorada de URL de playlist"""
    return any(x in url for x in ["&list=", "?list=", "/playlist?"])


async def play_next(ctx):
    """Toca a próxima música na fila"""
    guild_id = ctx.guild.id
    if guild_id in music_queues and music_queues[guild_id].queue:
        try:
            next_song = music_queues[guild_id].queue.popleft()

            if not next_song.audio_url:
                logger.info(f"Extraindo URL do áudio para: {next_song.title}")
                song_data = await extract_song_info(next_song.url)
                if song_data and song_data.audio_url:
                    next_song.audio_url = song_data.audio_url
                else:
                    await ctx.send(
                        f"⚠️ Não foi possível tocar {next_song.title}. Pulando..."
                    )
                    await play_next(ctx)
                    return

            player = discord.FFmpegOpusAudio(next_song.audio_url, **ffmpeg_options)
            voice_clients[guild_id].play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    play_next(ctx), client.loop
                ),
            )

            await ctx.send(f"🎵 Tocando agora: {next_song.title}")

        except Exception as e:
            logger.error(f"Erro em play_next: {e}")
            await ctx.send("⚠️ Erro ao tocar música atual, pulando para a próxima...")
            await play_next(ctx)
    else:
        await ctx.send("Fila está vazia!")


@client.command(name="playlist")
async def playlist_command(ctx, *, link):
    """Comando para tocar uma playlist"""
    try:
        if not ctx.author.voice:
            await ctx.send("❌ Você precisa estar em um canal de voz primeiro!")
            return

        if ctx.guild.id not in voice_clients:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
            logger.info(f"Conectado ao canal de voz no servidor {ctx.guild.id}")

        await process_playlist(ctx, link)

    except Exception as e:
        logger.error(f"Erro no comando playlist: {e}")
        await ctx.send(f"❌ Ocorreu um erro: {str(e)}")


@client.command(name="queue")
async def queue_status(ctx):
    """Mostra o status atual da fila"""
    guild_id = ctx.guild.id
    if guild_id in music_queues and music_queues[guild_id].queue:
        queue = music_queues[guild_id].queue
        status = "🎵 **Fila Atual:**\n"

        for i, song in enumerate(queue, 1):
            if i <= 10:  # Mostra apenas as primeiras 10 músicas
                status += f"{i}. {song.title}\n"

        if len(queue) > 10:
            status += f"\n... e mais {len(queue) - 10} músicas"

        await ctx.send(status)
    else:
        await ctx.send("A fila está vazia!")


@client.command(name="skip")
async def skip(ctx):
    """Pula para a próxima música"""
    guild_id = ctx.guild.id
    if guild_id in voice_clients:
        voice_clients[guild_id].stop()
        await ctx.send("⏭️ Pulando para a próxima música...")
    else:
        await ctx.send("Nada está tocando!")


@client.command(name="stop")
async def stop(ctx):
    """Para a reprodução e limpa a fila"""
    guild_id = ctx.guild.id
    if guild_id in voice_clients:
        if guild_id in music_queues:
            music_queues[guild_id].queue.clear()
        voice_clients[guild_id].stop()
        await voice_clients[guild_id].disconnect()
        del voice_clients[guild_id]
        await ctx.send("⏹️ Parou de tocar e limpou a fila!")
    else:
        await ctx.send("Nada está tocando!")


@client.command(name="pause")
async def pause(ctx):
    """Pausa a reprodução atual"""
    guild_id = ctx.guild.id
    if guild_id in voice_clients and voice_clients[guild_id].is_playing():
        voice_clients[guild_id].pause()
        await ctx.send("⏸️ Pausado!")
    else:
        await ctx.send("Nada está tocando!")


@client.command(name="resume")
async def resume(ctx):
    """Retoma a reprodução pausada"""
    guild_id = ctx.guild.id
    if guild_id in voice_clients and voice_clients[guild_id].is_paused():
        voice_clients[guild_id].resume()
        await ctx.send("▶️ Continuando!")
    else:
        await ctx.send("Nada está pausado!")


@client.event
async def on_voice_state_update(member, before, after):
    """Manipula eventos de mudança de estado de voz"""
    if member.id == client.user.id:  # Se o bot for o membro que mudou de estado
        if not after.channel:  # Se o bot foi desconectado
            guild_id = before.channel.guild.id
            if guild_id in music_queues:
                music_queues[guild_id].queue.clear()
            if guild_id in voice_clients:
                del voice_clients[guild_id]


# Executar o bot
client.run(TOKEN)
