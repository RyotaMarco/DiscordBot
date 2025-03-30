# Configurações do YouTube
YT_DL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "extract_flat": True,
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

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": '-vn -filter:a "volume=0.25"',
}

MAX_PLAYLIST_SIZE = 100  # Limita o número de músicas por playlist
MAX_QUEUE_DISPLAY = 10   # Número de músicas mostradas no comando de fila
THREAD_POOL_SIZE = 3     # Número máximo de threads para processamento em background