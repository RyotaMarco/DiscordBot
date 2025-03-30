"""
Módulo de comandos de música para o bot
"""
import asyncio
import discord
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
from utils.logger import setup_logger
from utils.music_queue import QueueManager, Song
from utils.youtube import (
    extract_song_info, 
    extract_playlist_info, 
    is_youtube_playlist
)
from config import FFMPEG_OPTIONS, MAX_QUEUE_DISPLAY, THREAD_POOL_SIZE

logger = setup_logger("music")

thread_pool = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)

class MusicCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.queue_manager = QueueManager()
        self.voice_clients = {}  
        
    async def connect_to_voice(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Você precisa estar em um canal de voz primeiro!")
            return None
            
        guild_id = ctx.guild.id
        
        if guild_id in self.voice_clients:
            return self.voice_clients[guild_id]
            
        try:
            voice_client = await ctx.author.voice.channel.connect()
            self.voice_clients[guild_id] = voice_client
            logger.info(f"Conectado ao canal de voz no servidor {ctx.guild.id}")
            return voice_client
        except Exception as e:
            logger.error(f"Erro ao conectar ao canal de voz: {e}")
            await ctx.send("❌ Não foi possível conectar ao canal de voz!")
            return None
    
    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        
        if guild_id not in self.voice_clients:
            return
            
        voice_client = self.voice_clients[guild_id]
        queue = self.queue_manager.get_queue(guild_id)
        
        if queue.is_empty():
            await ctx.send("🏁 Fila está vazia!")
            return
            
        next_song = queue.get_next()
        
        if not next_song:
            return
            
        try:
            if not next_song.audio_url:
                logger.info(f"Extraindo URL do áudio para: {next_song.title}")
                song_data = await extract_song_info(next_song.url)
                if song_data and song_data.audio_url:
                    next_song.audio_url = song_data.audio_url
                else:
                    await ctx.send(f"⚠️ Não foi possível tocar {next_song.title}. Pulando...")
                    await self.play_next(ctx)
                    return
            
            player = discord.FFmpegOpusAudio(next_song.audio_url, **FFMPEG_OPTIONS)
            voice_client.play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx), self.bot.loop
                )
            )
            
            await ctx.send(f"🎵 Tocando agora: {next_song.title}")
            
        except Exception as e:
            logger.error(f"Erro ao tocar música: {e}")
            await ctx.send(f"⚠️ Erro ao tocar música atual, pulando para a próxima...")
            await self.play_next(ctx)
            
    async def process_playlist(self, ctx, url):

        guild_id = ctx.guild.id
        queue = self.queue_manager.get_queue(guild_id)
        
        try:
            await ctx.send("🔍 Analisando playlist...")
            
            entries = await extract_playlist_info(url)
            
            if not entries:
                await ctx.send("❌ Não foi possível carregar a playlist ou está vazia.")
                return
                
            await ctx.send(f"📋 Encontradas {len(entries)} músicas!")
            
            first_entry = entries[0]
            first_url = first_entry.get("url") or f"https://www.youtube.com/watch?v={first_entry['id']}"
            
            first_song = await extract_song_info(first_url)
            
            if first_song:
                queue.add(first_song)
                await ctx.send(f"🎵 Começando com: {first_song.title}")
                
                voice_client = self.voice_clients.get(guild_id)
                if voice_client and not voice_client.is_playing():
                    await self.play_next(ctx)
            

            if len(entries) > 1:
                await ctx.send(f"⏳ Carregando mais {len(entries)-1} músicas em segundo plano...")
                asyncio.create_task(self.process_remaining_songs(ctx, entries[1:]))
                
        except Exception as e:
            logger.error(f"Erro ao processar playlist: {e}")
            await ctx.send(f"❌ Ocorreu um erro ao processar a playlist: {str(e)}")
            
    async def process_remaining_songs(self, ctx, entries):
        guild_id = ctx.guild.id
        queue = self.queue_manager.get_queue(guild_id)
        processed = 0
        failed = 0
        
        for entry in entries:
            try:
                if not entry:
                    continue
                    
                video_url = entry.get("url") or f"https://www.youtube.com/watch?v={entry['id']}"
                song = await extract_song_info(video_url)
                
                if song:
                    queue.add(song)
                    processed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Erro ao processar música: {e}")
                failed += 1
                
        await ctx.send(
            f"✅ Playlist processada!\n"
            f"✓ Músicas adicionadas: {processed}\n"
            f"✗ Falhas: {failed}"
        )
        
    @commands.command(name="play")
    async def play(self, ctx, *, url):
        if is_youtube_playlist(url):
            await self.playlist(ctx, link=url)
            return
            

        voice_client = await self.connect_to_voice(ctx)
        if not voice_client:
            return
            
        guild_id = ctx.guild.id
        queue = self.queue_manager.get_queue(guild_id)
        
        try:

            await ctx.send("🔍 Procurando música...")
            song = await extract_song_info(url)
            
            if not song:
                await ctx.send("❌ Não foi possível encontrar a música!")
                return
                

            queue.add(song)
            
            if not voice_client.is_playing():
                await self.play_next(ctx)
            else:
                await ctx.send(f"➕ Adicionado à fila: {song.title}")
                
        except Exception as e:
            logger.error(f"Erro ao processar comando play: {e}")
            await ctx.send(f"❌ Ocorreu um erro: {str(e)}")
            
    @commands.command(name="playlist")
    async def playlist(self, ctx, *, link):

        voice_client = await self.connect_to_voice(ctx)
        if not voice_client:
            return
            
        await self.process_playlist(ctx, link)
        
    @commands.command(name="queue")
    async def queue(self, ctx):

        guild_id = ctx.guild.id
        queue = self.queue_manager.get_queue(guild_id)
        
        if queue.is_empty() and not queue.current:
            await ctx.send("🔇 A fila está vazia!")
            return
            

        status = "🎵 **Fila Atual:**\n"
        

        if queue.current:
            status += f"▶️ **Tocando agora:** {queue.current.title}\n\n"
            

        if not queue.is_empty():
            status += "📋 **Próximas músicas:**\n"
            
            items = list(queue.queue)
            display_count = min(len(items), MAX_QUEUE_DISPLAY)
            
            for i in range(display_count):
                status += f"`{i+1}.` {items[i].title}\n"
                

            if len(items) > MAX_QUEUE_DISPLAY:
                status += f"\n... e mais {len(items) - MAX_QUEUE_DISPLAY} músicas"
        
        await ctx.send(status)
        
    @commands.command(name="skip")
    async def skip(self, ctx):

        guild_id = ctx.guild.id
        
        if guild_id not in self.voice_clients:
            await ctx.send("❌ Nada está tocando!")
            return
            
        voice_client = self.voice_clients[guild_id]
        
        if not voice_client.is_playing():
            await ctx.send("❌ Nada está tocando!")
            return
            
        voice_client.stop()
        await ctx.send("⏭️ Pulando para a próxima música...")
        
    @commands.command(name="stop")
    async def stop(self, ctx):

        guild_id = ctx.guild.id
        
        if guild_id not in self.voice_clients:
            await ctx.send("❌ Nada está tocando!")
            return
            
        
        self.queue_manager.get_queue(guild_id).clear()
        
     
        voice_client = self.voice_clients[guild_id]
        voice_client.stop()
        await voice_client.disconnect()
        
     
        del self.voice_clients[guild_id]
        self.queue_manager.remove_queue(guild_id)
        
        await ctx.send("⏹️ Parou de tocar e limpou a fila!")
        
    @commands.command(name="pause")
    async def pause(self, ctx):

        guild_id = ctx.guild.id
        
        if guild_id not in self.voice_clients:
            await ctx.send("❌ Nada está tocando!")
            return
            
        voice_client = self.voice_clients[guild_id]
        
        if voice_client.is_playing():
            voice_client.pause()
            await ctx.send("⏸️ Pausado!")
        else:
            await ctx.send("❌ Nada está tocando!")
            
    @commands.command(name="resume")
    async def resume(self, ctx):
        guild_id = ctx.guild.id
        
        if guild_id not in self.voice_clients:
            await ctx.send("❌ Nada está pausado!")
            return
            
        voice_client = self.voice_clients[guild_id]
        
        if voice_client.is_paused():
            voice_client.resume()
            await ctx.send("▶️ Continuando!")
        else:
            await ctx.send("❌ Nada está pausado!")
            
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if member.id == self.bot.user.id:
            if not after.channel:
                guild_id = before.channel.guild.id

                self.queue_manager.remove_queue(guild_id)
                if guild_id in self.voice_clients:
                    del self.voice_clients[guild_id]
                    
    @commands.command(name="volume")
    async def volume(self, ctx, volume: int = None):

        guild_id = ctx.guild.id
        
        if guild_id not in self.voice_clients:
            await ctx.send("❌ Nada está tocando!")
            return
            
        queue = self.queue_manager.get_queue(guild_id)
        
        if volume is None:
            current_vol = int(queue.volume * 100)
            await ctx.send(f"🔊 Volume atual: {current_vol}%")
            return
            

        if volume < 0 or volume > 100:
            await ctx.send("❌ O volume deve estar entre 0 e 100!")
            return
        queue.volume = volume / 100
        
        await ctx.send(f"🔊 Volume ajustado para {volume}%")