# DiscordBot

[![License](https://img.shields.io/github/license/RyotaMarco/DiscordBot)](LICENSE)
[![Stars](https://img.shields.io/github/stars/RyotaMarco/DiscordBot)](https://github.com/RyotaMarco/DiscordBot/stargazers)
[![Issues](https://img.shields.io/github/issues/RyotaMarco/DiscordBot)](https://github.com/RyotaMarco/DiscordBot/issues)

Um bot para Discord desenvolvido em Python, com funcionalidades diversas para ajudar a gerenciar servidores e oferecer ferramentas para interações divertidas e eficientes.

## Recursos

- **Comandos de administração:** Gerencie seu servidor com comandos de moderação eficazes.
- **Comandos de diversão:** Várias interações para manter os membros engajados.
- **Integrações personalizadas:** Fácil de expandir com novas funcionalidades.

## Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado em sua máquina:

- [Python](https://www.python.org/downloads/) (versão 3.8 ou superior)
- [pip](https://pip.pypa.io/en/stable/installation/) (gerenciador de pacotes do Python)
- [discord.py](https://discordpy.readthedocs.io/en/stable/) (biblioteca para interagir com a API do Discord)

## Instalação

Siga os passos abaixo para configurar e rodar o bot localmente:

1. Clone o repositório:
   ```bash
   git clone https://github.com/RyotaMarco/DiscordBot.git

2. Navegue até o diretório do projeto:
```bash
cd DiscordBot
```
3. Crie um ambiente virtual (opcional, mas recomendado):
 ```bash
Copiar código
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

4. instale as dependências:
 ```bash
Copiar código
pip install -r requirements.txt
 ```

5. Configure o arquivo .env com as credenciais do seu bot (crie este arquivo se ele não existir):
 ```makefile
Copiar código
DISCORD_TOKEN=seu_token_do_discord
PREFIX=!
 ```

6. Inicie o bot:
 ```bash
Copiar código
python bot.py
 ```

## Uso
Depois que o bot estiver online, você pode usar os seguintes comandos no seu servidor do Discord (ou conforme definidos no código do bot):

!play{Link}: Inicializa uma música.

!stop: Para a música.

!playlist{Link}: Baixa uma playlist e a inicializa. 
