import requests
import streamlit as st
from PIL import Image
import pytesseract
import mysql.connector
import os
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Gabriel\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def connect_to_db():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    conn.autocommit = True
    return conn

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calc_digito(digs):
        soma = sum(int(digs[i]) * (len(digs)+1-i) for i in range(len(digs)))
        d = 11 - soma % 11
        return '0' if d > 9 else str(d)

    d1 = calc_digito(cpf[:9])
    d2 = calc_digito(cpf[:9] + d1)
    return cpf[-2:] == d1 + d2

def cpf_ja_cadastrado(cpf: str) -> bool:
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM fans WHERE cpf = %s", (cpf,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

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

def save_social_profiles(fan_id, instagram):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
    INSERT INTO social_profiles (fan_id, instagram)
    VALUES (%s, %s)
    """
    values = (fan_id, instagram)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

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

st.set_page_config(page_title="Know Your Fan - eSports", layout="centered")
st.title("🎮 Know Your Fan - Cadastro de Fã de eSports")

menu = st.sidebar.radio("Escolha uma etapa", [
    "1️⃣ Dados Básicos",
    "2️⃣ Upload e Validação de Documento",
    "3️⃣ Redes Sociais",
    "4️⃣ Validação de Link de Perfil"
])

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
        if not validar_cpf(cpf):
            st.error("⚠️ CPF inválido. Verifique o número digitado.")
        elif cpf_ja_cadastrado(cpf):
            st.error("⚠️ CPF já cadastrado.")
        else:
            fan_id = save_fan_data(nome, cpf, endereco, interesses, eventos, compras)
            st.success(f"✅ Dados salvos! Fan ID: {fan_id}")
            st.write("Nome:", nome)
            st.write("Interesses:", interesses)
            st.session_state.fan_id = fan_id

elif menu == "2️⃣ Upload e Validação de Documento":
    st.header("🪪 Upload de Documento com IA")

    uploaded_file = st.file_uploader("Envie uma imagem do documento", type=["png", "jpg", "jpeg"])

    if uploaded_file:
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
                document_path = os.path.join("uploads", uploaded_file.name)
                os.makedirs(os.path.dirname(document_path), exist_ok=True)
                with open(document_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                save_document_image(fan_id, document_path)
                st.success("✅ Documento validado e salvo.")
            else:
                st.warning("⚠️ Documento pode não conter dados válidos.")

elif menu == "3️⃣ Redes Sociais":
    st.header("🔗 Redes Sociais")

    instagram = st.text_input("Perfil do Instagram")

    if st.button("Salvar Redes Sociais"):
        fan_id = st.session_state.get("fan_id")

        if fan_id is None:
            st.error("⚠️ Você precisa salvar seus dados básicos primeiro.")
        else:
            save_social_profiles(fan_id, instagram)
            st.success("✅ Redes sociais salvas.")
            st.write("Instagram:", instagram)

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
