from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import os
import random
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env (ex: token do bot)
load_dotenv()

# Obter o token do bot a partir das variáveis de ambiente
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Verificar se o token foi carregado corretamente
if not TOKEN:
    raise ValueError("O token do bot não foi configurado corretamente nas variáveis de ambiente.")

# Link para contato com a FURIA via WhatsApp
FURIA_CONTACT = "https://wa.me/5511993404466"

# Conjunto de usuários que se inscreveram para receber notificações
notificados = set()

# Mensagens de torcida para enviar ao usuário aleatoriamente
torcida_msgs = [
    "🔥 VAI FURIAAAA! 🔥",
    "💪 A FÚRIA NÃO PERDOA!",
    "🐍 RUMO AO MAJOR!",
    "💥 QUE BALA FOI ESSA, ART!?",
    "📣 VEM COM A GENTE, TORCEDOR!",
]

# Mensagem sobre o ranking atual da FURIA
ranking = "🌍 FURIA está atualmente em 8º lugar no ranking da HLTV."

# ----------- Comandos -----------

# Função que é chamada quando o usuário começa o bot (/start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Define o teclado com os botões que o usuário pode interagir
    keyboard = [
        [InlineKeyboardButton("🔔 Ativar Notificações", callback_data="ativar_notificacao")],
        [InlineKeyboardButton("🎮 Status", callback_data="status")],
        [InlineKeyboardButton("📅 Próximos Jogos", callback_data="proximos")],
        [InlineKeyboardButton("📰 Notícias", callback_data="noticias")],
        [InlineKeyboardButton("💬 Torcida", callback_data="torcida")],
        [InlineKeyboardButton("🏆 Ranking", callback_data="ranking")],
        [InlineKeyboardButton("📲 Contato", callback_data="contato")]
    ]
    # Cria o markup para o teclado
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Envia a mensagem inicial para o usuário com os botões
    await update.message.reply_text("🐍 Bem-vindo ao Chat dos Fãs da FURIA!", reply_markup=reply_markup)

# Função que lida com as ações dos botões (respostas das interações)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query  # Obtemos o objeto da consulta (callback query)
    await query.answer()  # Responde ao callback (necessário para evitar "espera infinita")
    user_id = query.from_user.id  # Pegamos o ID do usuário que interagiu

    # Verificamos o que o usuário clicou e tomamos a ação correspondente
    match query.data:
        case "ativar_notificacao":
            # Adiciona o usuário ao conjunto de notificados
            notificados.add(user_id)
            await query.message.reply_text("🔔 Notificações ativadas! Você será avisado sobre jogos e notícias.")
        case "status":
            # Envia uma mensagem sobre o status atual dos jogos
            await query.message.reply_text("🎮 Nenhum jogo rolando agora. Volte mais tarde!")
        case "proximos":
            # Envia a mensagem sobre o próximo jogo
            await query.message.reply_text("📅 Próximo jogo: FURIA x G2 - Sábado, 18h")
        case "noticias":
            # Envia a última notícia sobre a FURIA
            await query.message.reply_text("📰 Última notícia: FURIA vence confronto contra NAVI por 2x1!")
        case "torcida":
            # Envia uma mensagem de torcida aleatória
            await query.message.reply_text(random.choice(torcida_msgs))
        case "ranking":
            # Envia a mensagem sobre o ranking da FURIA
            keyboard = [
                [InlineKeyboardButton("Ver mais detalhes", url="https://www.hltv.org/team/8297/furia")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            # Envia a mensagem de ranking e o link para mais detalhes
            await query.message.reply_text(f"🏆 FURIA ocupa atualmente a 8ª posição no ranking da HLTV.", reply_markup=reply_markup)
        case "contato":
            # Envia o link de contato com a FURIA via WhatsApp
            await query.message.reply_text(f"📲 Fale com o suporte oficial: {FURIA_CONTACT}")

# Função que responde a mensagens de texto (permitindo conversas)
async def responder_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()  # Captura o texto enviado pelo usuário (em minúsculo para facilitar comparação)

    if "oi" in texto or "olá" in texto:
        await update.message.reply_text("👋 Olá! Como posso ajudar você a acompanhar a FURIA?")
    elif "notícia" in texto:
        await update.message.reply_text("📰 Última notícia: FURIA vence confronto contra NAVI por 2x1!")
    elif "jogo" in texto:
        await update.message.reply_text("📅 O próximo jogo é FURIA x G2, no sábado às 18h!")
    elif "torcida" in texto:
        await update.message.reply_text(random.choice(torcida_msgs))
    else:
        await update.message.reply_text("🤖 Desculpe, não entendi. Tente dizer 'notícia', 'jogo' ou 'torcida' para interagir!")

# Função para enviar alertas para os usuários inscritos (modo admin)
async def enviar_alerta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = "📣 ALERTA: FURIA joga hoje às 18h! Preparem os gritos de guerra!"
    # Envia a mensagem para todos os usuários que ativaram notificações
    for uid in notificados:
        try:
            await context.bot.send_message(chat_id=uid, text=mensagem)
        except:
            pass
    await update.message.reply_text("✅ Notificação enviada aos inscritos.")

# ----------- Main -----------

def main():
    # Inicializa o bot com o token
    app = ApplicationBuilder().token(TOKEN).build()

    # Adiciona os manipuladores de comando e interação
    app.add_handler(CommandHandler("start", start))  # Comando /start
    app.add_handler(CallbackQueryHandler(button_handler))  # Interações com os botões
    app.add_handler(MessageHandler(filters.TEXT, responder_mensagem))  # Responde às mensagens de texto
    app.add_handler(CommandHandler("enviar_alerta", enviar_alerta))  # Envio de alerta manual
    app.add_handler(CommandHandler("contato", lambda update, context: update.message.reply_text(f"📲 Fale com o suporte oficial: {FURIA_CONTACT}")))  # Comando /contato

    # Exibe no console que o bot está rodando
    print("Bot rodando com botões e notificações...")
    app.run_polling()  # Inicia o bot para começar a escutar as mensagens

# Função principal para executar o bot
if __name__ == "__main__":
    main()
