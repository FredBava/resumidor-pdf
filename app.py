import os
import openai
import streamlit as st
from dotenv import load_dotenv, find_dotenv
import PyPDF2

# Carrega as variáveis do .env
_ = load_dotenv(find_dotenv())
client = openai.Client()

st.set_page_config(page_title="Analisador de PDF com IA", layout="wide")
st.title("📄🔍 Analisador de PDF com IA")

# Função para extrair texto do PDF
def extrai_texto_pdf(uploaded_file):
    texto = ""
    leitor = PyPDF2.PdfReader(uploaded_file)
    for pagina in leitor.pages:
        texto += pagina.extract_text() or ''
    return texto.strip()

# Inicializa a sessão
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {"role": "system", "content": "Você é um assistente que responde perguntas com base no conteúdo de um PDF fornecido pelo usuário."}
    ]
if "conteudo_pdf" not in st.session_state:
    st.session_state.conteudo_pdf = ""

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Envie um arquivo PDF", type="pdf")

# Se um PDF for enviado, extrai o texto
if uploaded_file is not None:
    st.success("PDF carregado com sucesso!")
    texto_pdf = extrai_texto_pdf(uploaded_file)
    st.session_state.conteudo_pdf = texto_pdf

    # Adiciona o conteúdo ao histórico de mensagens (somente uma vez)
    if not any("Este é o conteúdo do PDF" in m["content"] for m in st.session_state.mensagens):
        st.session_state.mensagens.append(
            {"role": "user", "content": f"Este é o conteúdo do PDF:\n{texto_pdf}"}
        )

    # Caixa de pergunta do usuário
    pergunta = st.text_input("❓ Faça sua pergunta sobre o PDF")

    if st.button("📤 Enviar pergunta") and pergunta:
        st.session_state.mensagens.append({"role": "user", "content": pergunta})

        with st.spinner("Gerando resposta..."):
            resposta = client.chat.completions.create(
                messages=st.session_state.mensagens,
                model="gpt-4o",
                max_tokens=1000,
                temperature=0
            )
            resposta_ia = resposta.choices[0].message
            st.session_state.mensagens.append(resposta_ia.model_dump(exclude_none=True))
            st.success("✅ Resposta gerada:")
            st.write(resposta_ia.content)

    # Mostrar histórico da conversa (opcional)
    with st.expander("🕓 Histórico da conversa"):
        for msg in st.session_state.mensagens:
            if msg["role"] == "user":
                st.markdown(f"**Usuário:** {msg['content']}")
            elif msg["role"] == "assistant":
                st.markdown(f"**Assistente:** {msg['content']}")
else:
    st.info("Envie um PDF para começar.")
    