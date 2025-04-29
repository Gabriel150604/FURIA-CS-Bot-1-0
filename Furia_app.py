# Furia_app.py

import requests
import streamlit as st
from PIL import Image
import pytesseract
import mysql.connector
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Gabriel\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Conectar ao MySQL
def connect_to_db():
    conn = mysql.connector.connect(
        host="localhost",  # Endereço do seu servidor MySQL
        user="root",       # Seu usuário do MySQL
        password="1515",   # Sua senha do MySQL
        database="esports_fans"  # Nome do banco de dados
    )
    conn.autocommit = True  # Ativa o autocommit para garantir que as transações sejam salvas imediatamente
    return conn


# Função para salvar dados no banco
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
    fan_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return fan_id

# Função para salvar perfil de redes sociais
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

# Função para salvar o link do perfil
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

# Função para salvar imagem do documento
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

# Interface do app
st.set_page_config(page_title="Know Your Fan - eSports", layout="centered")
st.title("🎮 Know Your Fan - Cadastro de Fã de eSports")

menu = st.sidebar.radio("Escolha uma etapa", [
    "1️⃣ Dados Básicos",
    "2️⃣ Upload e Validação de Documento",
    "3️⃣ Redes Sociais",
    "4️⃣ Validação de Link de Perfil"
])

# --- Etapa 1: Dados Básicos ---
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
        st.session_state.fan_id = fan_id  # Armazenar o fan_id no session state

# --- Etapa 2: Upload e Validação de Documento ---
elif menu == "2️⃣ Upload e Validação de Documento":
    st.header("🪪 Upload de Documento com IA")

    uploaded_file = st.file_uploader("Envie uma imagem do documento", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        # Garantir que o fan_id esteja disponível
        fan_id = st.session_state.get("fan_id")

        if fan_id is None:
            st.error("⚠️ Você precisa salvar seus dados básicos primeiro.")
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption="Documento enviado", use_container_width=True)

            st.subheader("🔍 IA - OCR do Documento:")
            texto = pytesseract.image_to_string(image, lang='por')
            st.text_area("Texto detectado:", texto)

            if any(p in texto.lower() for p in ["cpf", "nome", "nascimento"]):
                # Salvar documento
                document_path = os.path.join("uploads", uploaded_file.name)
                os.makedirs(os.path.dirname(document_path), exist_ok=True)  # Cria o diretório, se necessário
                with open(document_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                save_document_image(fan_id, document_path)
                st.success("✅ Documento validado e salvo.")
            else:
                st.warning("⚠️ Documento pode não conter dados válidos.")

# --- Etapa 3: Redes Sociais ---
elif menu == "3️⃣ Redes Sociais":
    st.header("🔗 Redes Sociais")

    instagram = st.text_input("Perfil do Instagram")
    twitter = st.text_input("Perfil do Twitter/X")
    youtube = st.text_input("Canal do YouTube")

    if st.button("Salvar Redes Sociais"):
        fan_id = st.session_state.get("fan_id")

        if fan_id is None:
            st.error("⚠️ Você precisa salvar seus dados básicos primeiro.")
        else:
            save_social_profiles(fan_id, instagram, twitter, youtube)
            st.success("✅ Redes sociais salvas.")
            st.write("Instagram:", instagram)
            st.write("Twitter:", twitter)
            st.write("YouTube:", youtube)

# --- Etapa 4: Validação de Link de Perfil ---
elif menu == "4️⃣ Validação de Link de Perfil":
    st.header("🌐 Validação de Perfil em Sites de eSports")

    url = st.text_input("Cole aqui o link do seu perfil (ex: HLTV, Liquipedia, etc.)")

    if st.button("Validar Link"):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            texto = soup.get_text().lower()

            st.subheader("📄 Conteúdo da Página:")
            if any(p in texto for p in ["csgo", "valorant", "esports", "furia", "torneio"]):
                fan_id = st.session_state.get("fan_id")
                if fan_id is None:
                    st.error("⚠️ Você precisa salvar seus dados básicos primeiro.")
                else:
                    save_profile_link(fan_id, url)
                    st.success("✅ Link validado e salvo.")
            else:
                st.warning("⚠️ Conteúdo não aparenta ser relacionado a eSports.")
        except Exception as e:
            st.error(f"Erro ao acessar o link: {e}")
