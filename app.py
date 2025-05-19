import os
import openai
import streamlit as st
from dotenv import load_dotenv
import PyPDF2

# Configuração inicial do Streamlit
st.set_page_config(page_title="Analisador de PDF com IA", layout="wide")
st.title("📄🔍 Analisador de PDF com IA")

# Configuração segura do cliente OpenAI
def init_openai_client():
    try:
        # 1. Tenta usar secrets do Streamlit Cloud
        if "OPENAI_API_KEY" in st.secrets:
            return openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # 2. Fallback para variáveis de ambiente locais
        load_dotenv()
        if os.getenv("OPENAI_API_KEY"):
            return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 3. Erro se nenhuma chave for encontrada
        st.error("""
        🔐 Erro de configuração da API:
        1. Para local: Crie um arquivo .env ou .streamlit/secrets.toml
        2. Para nuvem: Adicione em Settings > Secrets no Streamlit Cloud
        """)
        st.stop()
        
    except Exception as e:
        st.error(f"Erro ao configurar a OpenAI: {str(e)}")
        st.stop()

client = init_openai_client()

# Função para extrair texto do PDF
def extrai_texto_pdf(uploaded_file):
    texto = ""
    try:
        leitor = PyPDF2.PdfReader(uploaded_file)
        for pagina in leitor.pages:
            texto += pagina.extract_text() or ''
        return texto.strip()
    except Exception as e:
        st.error(f"Erro ao ler PDF: {str(e)}")
        return ""

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
    if texto_pdf:  # Só continua se a extração foi bem-sucedida
        st.session_state.conteudo_pdf = texto_pdf

        # Adiciona o conteúdo ao histórico (somente uma vez)
        if not any("Este é o conteúdo do PDF" in m["content"] for m in st.session_state.mensagens):
            st.session_state.mensagens.append(
                {"role": "user", "content": f"Este é o conteúdo do PDF:\n{texto_pdf}"}
            )

        # Caixa de pergunta do usuário
        pergunta = st.text_input("❓ Faça sua pergunta sobre o PDF")

        if st.button("📤 Enviar pergunta") and pergunta:
            st.session_state.mensagens.append({"role": "user", "content": pergunta})

            with st.spinner("Gerando resposta..."):
                try:
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
                except openai.AuthenticationError:
                    st.error("Erro de autenticação. Verifique sua chave da OpenAI.")
                except Exception as e:
                    st.error(f"Erro ao gerar resposta: {str(e)}")

        # Mostrar histórico da conversa
        with st.expander("🕓 Histórico da conversa"):
            for msg in st.session_state.mensagens:
                if msg["role"] == "user":
                    st.markdown(f"**Usuário:** {msg['content']}")
                elif msg["role"] == "assistant":
                    st.markdown(f"**Assistente:** {msg['content']}")
else:
    st.info("Envie um PDF para começar.")