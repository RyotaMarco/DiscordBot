import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from utils.logger import setup_logger

logger = setup_logger("main")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    logger.error("Token do Discord não encontrado! Verifique o arquivo .env")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"{bot.user} está pronto e conectado!")
    
    try:
        from service.music import MusicCog
        await bot.add_cog(MusicCog(bot))
        logger.info("Módulo de música carregado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao carregar módulo de música: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Comando não encontrado!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Faltam argumentos para o comando!")
    else:
        logger.error(f"Erro no comando: {error}")
        await ctx.send(f"❌ Ocorreu um erro: {error}")

if __name__ == "__main__":
    bot.run(TOKEN)