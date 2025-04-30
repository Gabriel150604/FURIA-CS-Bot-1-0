# --- Bibliotecas utilizadas ---

import requests  # Usada para fazer requisições HTTP (ex: acessar links para validação de conteúdo)
import streamlit as st  # Criação da interface do usuário web
from PIL import Image  # Manipulação de imagens (upload e leitura de documentos)
import pytesseract  # OCR: reconhecimento de texto em imagens
import mysql.connector  # Conexão e manipulação de banco de dados MySQL
import os  # Interação com variáveis de ambiente e sistema de arquivos
from dotenv import load_dotenv  # Carrega variáveis de ambiente a partir de um arquivo .env
import tweepy  # Acesso à API do Twitter/X
from googleapiclient.discovery import build  # Acesso à API do YouTube
import json  # Manipulação de dados JSON (respostas de APIs)

# --- Carrega variáveis do arquivo .env ---
load_dotenv()

# Caminho para o executável do Tesseract OCR no Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Gabriel\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# --- Credenciais das APIs carregadas via .env ---
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# --- Função para conectar ao banco de dados MySQL ---
def connect_to_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# --- Função para salvar os dados principais do fã ---
def save_fan_data(nome, cpf, endereco, interesses, eventos, compras):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
    INSERT INTO fans (nome, cpf, endereco, interesses, eventos, compras)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (nome, cpf, endereco, interesses, eventos, compras)
    cursor.execute(query, values)
    conn.commit()
    fan_id = cursor.lastrowid  # Retorna o ID do novo fã inserido
    cursor.close()
    conn.close()
    return fan_id

# --- Função para salvar perfis de redes sociais ---
def save_social_profiles(fan_id, instagram, twitter, youtube):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
    INSERT INTO social_profiles (fan_id, instagram, twitter, youtube)
    VALUES (%s, %s, %s, %s)
    """
    values = (fan_id, instagram, twitter, youtube)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

# --- Função para salvar links de perfis externos ---
def save_profile_link(fan_id, url):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
    INSERT INTO profile_links (fan_id, url)
    VALUES (%s, %s)
    """
    values = (fan_id, url)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

# --- Função para salvar imagem de documento enviado ---
def save_document_image(fan_id, document_image_path):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
    INSERT INTO documents (fan_id, document_image_path)
    VALUES (%s, %s)
    """
    values = (fan_id, document_image_path)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

# --- Função para validar se o link é relevante (usando palavras-chave eSports) ---
def validate_link_content(url):
    try:
        response = requests.get(url, timeout=10)
        content = response.text.lower()
        if any(keyword in content for keyword in ["csgo", "valorant", "esports", "furia", "torneio"]):
            return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o link: {e}")
        return False

# --- Função para obter dados do Twitter ---
def get_twitter_data(username):
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY, 
        TWITTER_API_SECRET, 
        TWITTER_ACCESS_TOKEN, 
        TWITTER_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)
    user = api.get_user(screen_name=username)
    tweets = api.user_timeline(screen_name=username, count=10)
    return user, tweets

# --- Função para obter dados do YouTube ---
def get_youtube_data(channel_id):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.channels().list(part="snippet,contentDetails,statistics", id=channel_id)
    response = request.execute()
    return response

# --- Função para obter dados do Instagram (via API do Graph) ---
def get_instagram_data(instagram_username):
    headers = {
        "Authorization": f"Bearer {INSTAGRAM_ACCESS_TOKEN}"
    }
    response = requests.get(f"https://graph.instagram.com/{instagram_username}/media", headers=headers)
    return response.json()

# --- Interface Gráfica (UI) com Streamlit ---

st.set_page_config(page_title="Furia - eSports", layout="centered")
st.title("🎮 Furia - Cadastro de Fã de eSports")

# Menu lateral com as etapas do cadastro
menu = st.sidebar.radio("Escolha uma etapa", [
    "1️⃣ Dados Básicos",
    "2️⃣ Upload e Validação de Documento",
    "3️⃣ Redes Sociais",
    "4️⃣ Validação de Link de Perfil"
])

# --- Etapa 1: Coleta de dados pessoais e interesses ---
if menu == "1️⃣ Dados Básicos":
    st.header("📋 Dados Pessoais e Interesses")

    nome = st.text_input("Nome completo")
    cpf = st.text_input("CPF")
    endereco = st.text_input("Endereço completo")

    st.subheader("🎯 Interesses e Atividades")
    interesses = st.text_area("Quais são seus interesses em eSports?")
    eventos = st.text_input("Eventos que participou no último ano")
    compras = st.text_input("Produtos/serviços de eSports comprados")

    if st.button("Salvar Dados"):
        fan_id = save_fan_data(nome, cpf, endereco, interesses, eventos, compras)
        st.success(f"✅ Dados salvos! Fan ID: {fan_id}")
        st.write("Nome:", nome)
        st.write("Interesses:", interesses)

# --- Etapa 2: Upload de documento e OCR com IA ---
elif menu == "2️⃣ Upload e Validação de Documento":
    st.header("🪪 Upload de Documento com IA")

    uploaded_file = st.file_uploader("Envie uma imagem do documento", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Documento enviado", use_container_width=True)

        st.subheader("🔍 IA - OCR do Documento:")
        texto = pytesseract.image_to_string(image, lang='por')
        st.text_area("Texto detectado:", texto)

        if any(p in texto.lower() for p in ["cpf", "nome", "nascimento"]):
            document_path = os.path.join("uploads", uploaded_file.name)
            with open(document_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            save_document_image(fan_id, document_path) # type: ignore
            st.success("✅ Documento validado e salvo.")
        else:
            st.warning("⚠️ Documento pode não conter dados válidos.")

# --- Etapa 3: Vinculação de redes sociais e leitura de dados ---
elif menu == "3️⃣ Redes Sociais":
    st.header("🔗 Redes Sociais")

    instagram = st.text_input("Perfil do Instagram")
    twitter = st.text_input("Perfil do Twitter/X")
    youtube = st.text_input("Canal do YouTube")

    if st.button("Salvar Redes Sociais"):
        save_social_profiles(fan_id, instagram, twitter, youtube) # type: ignore
        st.success("✅ Redes sociais salvas.")
        st.write("Instagram:", instagram)
        st.write("Twitter:", twitter)
        st.write("YouTube:", youtube)

        twitter_user, twitter_tweets = get_twitter_data(twitter)
        st.write(f"Últimos tweets de {twitter_user.screen_name}:")
        for tweet in twitter_tweets:
            st.write(f"- {tweet.text}")

        youtube_data = get_youtube_data(youtube)
        st.write(f"Dados do canal YouTube {youtube_data['items'][0]['snippet']['title']}:")
        st.write(f"Subscribers: {youtube_data['items'][0]['statistics']['subscriberCount']}")

        instagram_data = get_instagram_data(instagram)
        st.write(f"Dados do Instagram: {instagram_data}")

# --- Etapa 4: Validação de link externo ---
elif menu == "4️⃣ Validação de Link de Perfil":
    st.header("🌐 Validação de Perfil em Sites de eSports")

    url = st.text_input("Cole aqui o link do seu perfil (ex: HLTV, Liquipedia, etc.)")

    if st.button("Validar Link"):
        if validate_link_content(url):
            save_profile_link(fan_id, url) # type: ignore
            st.success("✅ Link validado e salvo.")
        else:
            st.warning("⚠️ Conteúdo não aparenta ser relacionado a eSports.")
