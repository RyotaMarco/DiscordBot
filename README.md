# Discord Music Bot

Este é um bot de música para Discord desenvolvido em Python, que utiliza yt-dlp para reproduzir músicas diretamente do YouTube. O projeto foi hospedado na AWS EC2 para garantir alta disponibilidade e inclui uma automação em Windows para facilitar a troca de cookies ao acessar playlists protegidas.

> **Nota**: Este projeto foi criado 100% para fins educacionais, com o objetivo de aprender sobre integração com APIs, automação e hospedagem de aplicações.

---

## 🚀 Funcionalidades

- 📋 Toca playlists ou músicas individuais do YouTube no Discord.
- 🔎 Suporte a buscas por palavras-chave no YouTube.
- ⏯️ Comandos para controle de reprodução, como `play`, `pause`, `resume`, `stop` e `skip`.
- 📂 Fila de reprodução dinâmica.
- 🔧 Hospedagem na AWS EC2 para alta disponibilidade.
- 🤖 Automação em Windows para atualização de cookies e acesso a conteúdos protegidos.
- 🎧 Configuração de volume personalizada.

---

## 🔦 Tecnologias Utilizadas

- **Python 3.8+**
- **Discord.py**: Para a criação do bot no Discord.
- **yt-dlp**: Para extração e streaming de áudio do YouTube.
- **AWS EC2**: Para hospedar o bot e garantir sua disponibilidade 24/7.
- **dotenv**: Para gerenciar variáveis de ambiente de forma segura.
- **FFmpeg**: Para processamento de áudio.
- **Windows Automation**: Scripts de automação para troca de cookies.

---

## 🔧 Configuração e Uso

### Pré-requisitos

- Python 3.8 ou superior instalado.
- FFmpeg instalado e configurado no PATH do sistema.
- Conta na AWS com uma instância EC2 configurada (opcional para hospedagem).

### Instalação Local

1. Clone este repositório:

    ```bash
    git clone https://github.com/seuusuario/seurepositorio.git
    cd seurepositorio
    ```

2. Crie um ambiente virtual e ative:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate    # Windows
    ```

3. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

4. Crie um arquivo `.env` com o token do bot e outras variáveis de ambiente:

    ```env
    DISCORD_TOKEN=seu_token_do_bot
    ```

5. Adicione um arquivo de cookies na raiz do projeto (por exemplo, `cookies.txt`).

6. Execute o bot:

    ```bash
    python main.py
    ```

---

## 🗋 Comandos Disponíveis

### 🎵 Música

- `.play`: Reproduz uma música ou playlist.
- `.pause`: Pausa a música atual.
- `.resume`: Retoma a música pausada.
- `.skip`: Pula para a próxima música na fila.
- `.stop`: Para a música e limpa a fila.
- `.queue`: Mostra as músicas na fila.

### 🔍 Status

- `.ping`: Verifica se o bot está online.

---

## ☁️ Hospedagem na AWS EC2

O bot está hospedado em uma instância EC2, garantindo disponibilidade contínua. Foi configurado para iniciar automaticamente junto ao sistema operacional da instância.

---

## 🤖 Automação no Windows

Para acessar playlists protegidas ou privadas no YouTube, desenvolvi uma automação que facilita a troca de cookies de autenticação. Essa automação garante que o bot funcione sem interrupções em conteúdos protegidos.

---

## 📚 Aprendizados

Este projeto foi uma excelente oportunidade para aprender e aplicar conceitos como:

- Integração com APIs (Discord e YouTube).
- Automação de tarefas no Windows.
- Configuração e gerenciamento de servidores na AWS EC2.
- Manipulação de dados com yt-dlp e processamento de áudio com FFmpeg.

---

## ⚠️ Avisos

Este projeto foi desenvolvido exclusivamente para fins educacionais. **Não deve ser utilizado para violar os Termos de Serviço de plataformas como YouTube ou Discord.**
