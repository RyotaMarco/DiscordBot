# Discord Music Bot

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)

Um bot para Discord desenvolvido em Python, especializado em reprodução de música com funcionalidades avançadas como equalizador, pesquisa, e gerenciamento de playlists.

## 🎵 Recursos

- **Player de Música Avançado**
  - Reprodução de músicas do YouTube
  - Processamento otimizado de playlists
  - Sistema de filas com navegação completa
  - Comandos de controle (play, pause, skip, stop)

- **Controle de Áudio**
  - Equalizador com presets configuráveis (bass boost, nightcore, 8D)
  - Ajuste de volume
  - Efeitos de áudio diversos

- **Pesquisa Inteligente**
  - Suporte para links do YouTube, links encurtados e playlists
  - Pesquisa direta por termos no YouTube
  - Interface de seleção para resultados de busca

- **Gerenciamento de Fila**
  - Visualização detalhada da fila atual
  - Remoção e movimentação de músicas
  - Embaralhamento da fila
  - Limpar fila mantendo a música atual

## 📋 Pré-requisitos

- [Python](https://www.python.org/downloads/) (versão 3.8 ou superior)
- [pip](https://pip.pypa.io/en/stable/installation/) (gerenciador de pacotes do Python)
- [FFmpeg](https://ffmpeg.org/download.html) (instalado e disponível no PATH)
- Um [token de bot do Discord](https://discord.com/developers/applications)

## ⚙️ Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/discord-music-bot.git
   cd discord-music-bot
   ```

2. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   
   # Ativar no Windows
   venv\Scripts\activate
   
   # Ativar no Linux/macOS
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Copie o arquivo `.env.example` para `.env` e configure seu token:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com seu editor favorito
   ```

5. Inicie o bot:
   ```bash
   python main.py
   ```

## 🤖 Comandos

| Comando | Descrição |
|---------|-----------|
| `.play <url/termo>` | Reproduz uma música ou adiciona à fila |
| `.playlist <url>` | Carrega uma playlist do YouTube |
| `.search <termo>` | Busca no YouTube e permite selecionar um resultado |
| `.queue` | Mostra a fila atual de reprodução |
| `.skip` | Pula para a próxima música |
| `.stop` | Para a reprodução e limpa a fila |
| `.pause` | Pausa a reprodução atual |
| `.resume` | Retoma a reprodução pausada |
| `.np` | Mostra detalhes da música atual |
| `.volume <0-100>` | Ajusta o volume de reprodução |
| `.eq <preset>` | Define o preset do equalizador |
| `.bass` | Atalho para ativar/desativar bass boost |
| `.nightcore` | Ativa o efeito nightcore |
| `.8d` | Ativa o efeito de áudio 8D |
| `.remove <posição>` | Remove uma música específica da fila |
| `.move <de> <para>` | Move uma música na fila |
| `.shuffle` | Embaralha a fila de reprodução |
| `.clear` | Limpa a fila (mantém a música atual) |
| `.lyrics [música]` | Busca letra da música atual ou especificada |

## 🔧 Configuração Avançada

Você pode personalizar o comportamento do bot editando o arquivo `config.py`:

- Prefixo de comandos
- Configurações do FFmpeg
- Presets de equalizador
- Limites de fila e playlists
- Níveis de log

## 🏗️ Estrutura do Projeto

```
discord-music-bot/
├── main.py                # Ponto de entrada principal
├── config.py              # Configurações globais
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente (token)
├── cogs/                  # Módulos de comandos
│   ├── music.py           # Comandos de música
│   └── help.py            # Sistema de ajuda
└── utils/                 # Funções utilitárias
    ├── logger.py          # Configuração de logs
    ├── music_queue.py     # Gerenciamento de filas
    ├── youtube.py         # Interação com YouTube
    └── playlist_processor.py # Processamento de playlists
```

## 📝 Notas

- O bot requer permissões para acessar canais de voz e enviar mensagens
- O streaming de música depende da biblioteca FFmpeg instalada corretamente
- O desempenho pode variar dependendo da conexão à internet e capacidade do servidor

## 📜 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests para melhorar o bot.
