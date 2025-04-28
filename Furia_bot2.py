import os
import logging
import requests
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    JobQueue,
)
from datetime import time

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not TOKEN or not NEWS_API_KEY:
    raise ValueError("Os tokens não foram configurados corretamente nas variáveis de ambiente.")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# /start com botões interativos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Envia uma mensagem de boas-vindas com botões interativos para o usuário.
    """
    keyboard = [
        [InlineKeyboardButton("📰 Notícias", callback_data='noticias')],
        [InlineKeyboardButton("🎮 Próximo Jogo", callback_data='proximo_jogo')],
        [InlineKeyboardButton("👥 Elenco", callback_data='elenco')],
        [InlineKeyboardButton("📈 Ranking", callback_data='ranking')],
        [InlineKeyboardButton("❓ Quiz", callback_data='quiz')],
        [InlineKeyboardButton("🆘 Ajuda", callback_data='ajuda')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bem-vindo ao FURIA CS Bot! Escolha uma opção:", reply_markup=reply_markup)

# /noticias com fallback
async def noticias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    def buscar_noticias(lang):
        url = (
            "https://newsapi.org/v2/everything?q=FURIA%20esports%20OR%20FURIA%20Counter-Strike&"
            f"language={lang}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        )
        return requests.get(url, timeout=10)  # Adiciona timeout para evitar travamentos

    try:
        response = buscar_noticias("pt")
        response.raise_for_status()  # Verifica se a resposta HTTP foi bem-sucedida
        artigos = response.json().get('articles', [])[:5]
        if not artigos:
            response = buscar_noticias("en")
            response.raise_for_status()
            artigos = response.json().get('articles', [])[:5]
            if not artigos:
                await update.callback_query.message.reply_text("Nenhuma notícia recente encontrada sobre a FURIA.")
                return
            intro = "📰 Últimas notícias da FURIA (em inglês):\n\n"
        else:
            intro = "📰 Últimas notícias da FURIA:\n\n"
        texto = intro
        for artigo in artigos:
            texto += f"• {artigo.get('title', 'Sem título')}\n{artigo.get('url', '')}\n\n"
        await update.callback_query.message.reply_text(texto)
    except requests.exceptions.RequestException as e:
        await update.callback_query.message.reply_text(f"Erro ao buscar notícias: {e}")
    except Exception as e:
        await update.callback_query.message.reply_text("Ocorreu um erro inesperado. Tente novamente mais tarde.")

# /proximo_jogo com integração da Liquipedia API
async def proximo_jogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Busca informações sobre o próximo jogo da FURIA usando a Liquipedia API.
    """
    url = "https://liquipedia.net/counterstrike/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": "FURIA",
        "format": "json"
    }
    headers = {
        "User-Agent": "FURIA-CS-Bot/1.0 (https://github.com/seu-repositorio)"
    }

    try:
        # Faz a requisição à API
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Verifica se a resposta HTTP foi bem-sucedida
        data = response.json()

        # Verifica se há resultados
        resultados = data.get("query", {}).get("search", [])
        if not resultados:
            await update.callback_query.message.reply_text("Nenhum jogo futuro encontrado para a FURIA.")
            return

        # Itera sobre os resultados e formata a mensagem
        texto = "🎮 **Resultados da Pesquisa sobre a FURIA**:\n\n"
        for resultado in resultados:
            titulo = resultado.get("title", "Título não disponível")
            snippet = resultado.get("snippet", "Descrição não disponível").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
            pageid = resultado.get("pageid")
            link = f"https://liquipedia.net/counterstrike/index.php?curid={pageid}"

            texto += f"🔹 **{titulo}**\n{snippet}\n[Mais detalhes]({link})\n\n"

        # Envia a mensagem com os resultados
        await update.callback_query.message.reply_text(texto, parse_mode="Markdown")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição: {e}")
        await update.callback_query.message.reply_text(f"Erro ao buscar informações do próximo jogo: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        await update.callback_query.message.reply_text("Ocorreu um erro inesperado. Tente novamente mais tarde.")
# /elenco com imagens e fallback de contexto
async def elenco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    elenco_info = [
        ("KSCERATO - Rifler", "https://imgs.search.brave.com/dKjlaA4UCFHNE5QZYMXOEma0u3zzCZ63XExnf1VkFLI/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9wcm9m/aWxlcnIubmV0L3N0/YXRpYy9jb250ZW50/L3RodW1icy8zMzV4/MzM1L2MvYTAvM2p0/dm9mLS0tYzF4MXgy/MDBweDBwLXJjLS1j/NTZhNWM3NjQ5NDRh/YTJjNGViOTViM2Jk/ZTc5NWEwYy5wbmc"),
        ("yuurih - Entry Fragger", "https://imgs.search.brave.com/bfecMBYuoSD1xGu5Aw4RMGe96RCCVpiP9TWdVLKD7Eo/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9saXF1/aXBlZGlhLm5ldC9j/b21tb25zL2ltYWdl/cy90aHVtYi9hL2E2/L1l1dXJpaF9hdF9Q/R0xfQnVjaGFyZXN0/XzIwMjUuanBnLzYw/MHB4LVl1dXJpaF9h/dF9QR0xfQnVjaGFy/ZXN0XzIwMjUuanBn"),
        ("FalleN - IGL / AWP", "https://imgs.search.brave.com/imHrrz-wNG31WRtmywy68Dgj4XODeGN4omB8CPJggTk/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly91cGxv/YWQud2lraW1lZGlh/Lm9yZy93aWtpcGVk/aWEvY29tbW9ucy90/aHVtYi9lL2U3L0Zh/bGxlTl9JRU1fQ2hp/Y2Fnb18lMjg0ODM1/MzcwODgxMiUyOV8l/Mjhjcm9wcGVkJTI5/LmpwZy81MTJweC1G/YWxsZU5fSUVNX0No/aWNhZ29fJTI4NDgz/NTM3MDg4MTIlMjlf/JTI4Y3JvcHBlZCUy/OS5qcGc"),
        ("chelo - Support", "https://imgs.search.brave.com/0HuxcrWwcqbVRybyj0f1jZyZlz8COcA6g6p7fJdEvuA/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9hc3Nl/dHMuZ2FtZWFyZW5h/LmdnL3dwLWNvbnRl/bnQvdXBsb2Fkcy8y/MDI1LzAyLzA1MDk1/NDA3L2NoZWxvLUhl/bGVuYS1LcmlzdGlh/bnNzb24tMTAyNHg2/ODMuanBn"),
        ("arT - Lurker", "https://imgs.search.brave.com/_8lJrD5inonBes4X5ULaU0qPxAvjl2AQ02Ap_doAPo4/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly93d3cu/MzY1c2NvcmVzLmNv/bS9wdC1ici9uZXdz/L21hZ2F6aW5lL3dw/LWNvbnRlbnQvdXBs/b2Fkcy8yMDI0LzA0/L2lvNWQ5UFN5eFA2/bGx5THdyNnNTMDUt/c2NhbGVkLmpwZw"),
        ("guerri: Coach", "https://imgs.search.brave.com/Wr2g0B_iAKTh48jo3S0HBj0WB-JHeL9TnzEYLSXMaHU/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5hc3NldHR5cGUu/Y29tL2Fma2dhbWlu/Zy8yMDIxLTA5L2E1/MWJjYjk1LTQ3MTIt/NDdlYy04MDVkLWFh/MjY5NzdjMDNhZS9D/b3Zlcl9JbWFnZV9f/X0ZVUklBX0NTR09f/Q29hY2hfR3VlcnJp/X1ByYWlzZWRfQnlf/VGVhbXNfX1BsYXll/cnNfRm9yX0hpc19Q/ZXJmb3JtYW5jZS5q/cGc_cmVjdD0wLDAs/MTEyMCw2MzAmYXV0/bz1mb3JtYXQsY29t/cHJlc3MmZHByPTEu/MCZ3PTEyMDA")
    ]
    for nome, img_url in elenco_info:
        if update.callback_query:
            await update.callback_query.message.reply_photo(photo=img_url, caption=nome)
        elif update.message:
            await update.message.reply_photo(photo=img_url, caption=nome)

# /ranking
async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📈 **Ranking Atual da FURIA**:\n"
        "Posição: **12º** no ranking mundial da HLTV\n"
        "Última atualização: **Abril de 2025**\n\n"
        "Outras informações relevantes sobre a FURIA no ranking:\n"
        "🔸 Melhor posição histórica: **2º lugar** em 2020\n"
        "🔸 Pontuação atual: **890** pontos\n"
        "🔸 Desempenho recente: VITÓRIA contra a Team Liquid na última partida!\n\n"
        "Fique atento às atualizações e próximos jogos da nossa FURIA!"
    )
    await update.callback_query.message.reply_text(texto, parse_mode="Markdown")

# /quiz - Inicia o quiz
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    perguntas = [
        {"pergunta": "Quem é o capitão da FURIA?", "respostas": ["FalleN", "arT", "yuurih"], "correta": "arT"},
        {"pergunta": "Em que ano a FURIA foi fundada?", "respostas": ["2015", "2016", "2017"], "correta": "2017"},
        {"pergunta": "Qual é o nome do treinador da FURIA?", "respostas": ["guerri", "zews", "golden"], "correta": "guerri"},
    ]

    pergunta = random.choice(perguntas)
    context.user_data['quiz'] = pergunta

    teclado_respostas = [
        [InlineKeyboardButton(resposta, callback_data=f"quiz:{resposta}")]
        for resposta in pergunta['respostas']
    ]
    reply_markup = InlineKeyboardMarkup(teclado_respostas)

    texto = f"❓ {pergunta['pergunta']}\nEscolha uma resposta:"
    if update.message:
        await update.message.reply_text(texto, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(texto, reply_markup=reply_markup)

# /verificar_resposta - Verifica a resposta do usuário
async def verificar_resposta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if 'quiz' not in context.user_data:
        await query.message.reply_text("Não há um quiz ativo no momento. Use /quiz para começar.")
        return

    resposta_selecionada = query.data.split(":")[1]
    pergunta = context.user_data['quiz']
    correta = pergunta['correta']

    if resposta_selecionada == correta:
        feedback = "✅ Resposta correta! 🎉"
    else:
        feedback = f"❌ Errado! A resposta correta era: {correta}."

    keyboard = [
        [InlineKeyboardButton("🔄 Tentar outra pergunta", callback_data='quiz')],
        [InlineKeyboardButton("🏠 Voltar ao menu principal", callback_data='start')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(f"{feedback}\n\nDeseja continuar?", reply_markup=reply_markup)
    del context.user_data['quiz']

# Ajuda
async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "🆘 *Ajuda - FURIA CS Bot*\n\n"
        "Este bot oferece as seguintes funções:\n"
        "• 📰 *Notícias* – últimas notícias da equipe FURIA.\n"
        "• 🎮 *Próximo Jogo* – data, hora e adversário da próxima partida.\n"
        "• 👥 *Elenco* – veja o elenco atual com imagens.\n"
        "• 📈 *Ranking* – posição atual da FURIA no ranking HLTV.\n"
        "• ❓ *Quiz* – teste seus conhecimentos sobre a FURIA.\n"
        "• 🔔 *Notificações* – receba alertas diários sobre notícias novas.\n\n"
        "Use o botão correspondente ou envie o comando diretamente."
    )
    await update.callback_query.message.reply_text(texto, parse_mode="Markdown")

# Handler de botões
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("quiz:"):
        await verificar_resposta(update, context)
    else:
        match query.data:
            case 'noticias': await noticias(update, context)
            case 'proximo_jogo': await proximo_jogo(update, context)
            case 'elenco': await elenco(update, context)
            case 'ranking': await ranking(update, context)
            case 'quiz': await quiz(update, context)
            case 'ajuda': await ajuda(update, context)

# Alerta de notícias
async def alerta_noticias(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    url = f"https://newsapi.org/v2/everything?q=FURIA%20esports&language=pt&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        artigos = response.json().get("articles", [])
        if artigos:
            artigo = artigos[0]
            texto = f"🛎️ Alerta de notícia nova:\n{artigo['title']}\n{artigo['url']}"
            await context.bot.send_message(chat_id=chat_id, text=texto)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Erro ao buscar alertas: {e}")

# Main
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("quiz", quiz))

    async def agendar_alerta(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        context.job_queue.run_daily(alerta_noticias, time=time(hour=12), chat_id=chat_id, name=str(chat_id))
        await update.message.reply_text("🔔 Notificações diárias ativadas! Você receberá alertas às 12h com as últimas notícias.")

    app.add_handler(CommandHandler("notificacoes", agendar_alerta))
    app.run_polling()

if __name__ == '__main__':
    main()