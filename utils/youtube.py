
import asyncio
import yt_dlp
from utils.logger import setup_logger
from utils.music_queue import Song
from config import YT_DL_OPTIONS

logger = setup_logger("youtube")

def is_youtube_url(url):

    return "youtube.com" in url or "youtu.be" in url

def is_youtube_playlist(url):

    return any(x in url for x in ["&list=", "?list=", "/playlist?"])

def extract_playlist_id(url):

    if "list=" in url:
        return url.split("list=")[1].split("&")[0]
    return None

async def extract_song_info(url):

    loop = asyncio.get_event_loop()
    try:
        logger.info(f"Extraindo informações da música: {url}")
        
        single_options = YT_DL_OPTIONS.copy()
        single_options["noplaylist"] = True
        
        with yt_dlp.YoutubeDL(single_options) as ydl:
            try:
                data = await loop.run_in_executor(
                    None, lambda: ydl.extract_info(url, download=False)
                )
                
                if not data:
                    logger.error(f"Nenhum dado extraído para URL: {url}")
                    return None
                
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

async def extract_playlist_info(url, limit=100):

    try:
        logger.info(f"Extraindo informações da playlist: {url}")
        
        playlist_options = {
            "extract_flat": True,
            "quiet": True,
            "ignoreerrors": True,
            "no_warnings": True,
            "playlistend": limit,
        }
        
        with yt_dlp.YoutubeDL(playlist_options) as ydl:
            playlist_info = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ydl.extract_info(url, download=False)
            )
            
            if not playlist_info:
                logger.error("Não foi possível carregar a playlist.")
                return None
            
            if "entries" in playlist_info:
                entries = list(filter(None, playlist_info["entries"]))
                return entries
            else:
                return [playlist_info]
    except Exception as e:
        logger.error(f"Erro ao extrair informações da playlist: {str(e)}")
        return None