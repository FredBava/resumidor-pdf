import os
import openai
import streamlit as st
from dotenv import load_dotenv
import PyPDF2
import traceback

# Configuração inicial do Streamlit
st.set_page_config(page_title="Analisador de PDF com IA", layout="wide")
st.title("📄🔍 Analisador de PDF com IA")

# Configuração segura do cliente OpenAI
def init_openai_client():
    try:
        # 1. Tenta usar secrets do Streamlit Cloud
        if "OPENAI_API_KEY" in st.secrets:
            st.success("Usando chave do Streamlit Secrets")
            return openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # 2. Fallback para variáveis de ambiente locais
        load_dotenv()
        local_key = os.getenv("OPENAI_API_KEY")
        if local_key:
            st.success("Usando chave do arquivo .env")
            return openai.OpenAI(api_key=local_key)
        
        # 3. Erro se nenhuma chave for encontrada
        st.error("""
        🔐 Erro de configuração da API:
        1. Para local: Crie um arquivo .env ou .streamlit/secrets.toml com OPENAI_API_KEY
        2. Para nuvem: Adicione em Settings > Secrets no Streamlit Cloud
        """)
        st.link_button("Gerenciar Chaves OpenAI", "https://platform.openai.com/api-keys")
        st.stop()
        
    except Exception as e:
        st.error(f"Erro crítico ao configurar a OpenAI: {str(e)}")
        st.stop()

client = init_openai_client()

# Função para extrair texto do PDF com validação
def extrai_texto_pdf(uploaded_file):
    try:
        if uploaded_file.type != "application/pdf":
            st.error("Por favor, envie um arquivo PDF válido")
            return ""
            
        leitor = PyPDF2.PdfReader(uploaded_file)
        if len(leitor.pages) > 20:  # Limite de páginas
            st.warning("⚠️ PDF muito grande (máx 20 páginas). Processando parcialmente...")
            
        texto = "".join(page.extract_text() or '' for page in leitor.pages[:20])
        return texto.strip() if texto else ""
        
    except PyPDF2.PdfReadError:
        st.error("❌ PDF corrompido ou protegido por senha")
        return ""
    except Exception as e:
        st.error(f"Erro inesperado ao ler PDF: {str(e)}")
        return ""

# Inicializa a sessão com limpeza automática
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {"role": "system", "content": "Você é um assistente especialista em análise de documentos. Responda com precisão sobre o conteúdo do PDF fornecido."}
    ]
    
if "conteudo_pdf" not in st.session_state:
    st.session_state.conteudo_pdf = ""

# Interface principal
with st.sidebar:
    st.header("Configurações")
    model_name = st.selectbox("Modelo", ["gpt-4o", "gpt-4-turbo"], index=0)
    max_tokens = st.slider("Tamanho da resposta", 500, 2000, 1000)
    st.caption(f"Versão: {openai.__version__}")

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Envie um arquivo PDF (máx. 20 páginas)", type="pdf")

if uploaded_file is not None:
    with st.spinner("Processando PDF..."):
        texto_pdf = extrai_texto_pdf(uploaded_file)
        
    if texto_pdf:
        st.session_state.conteudo_pdf = texto_pdf
        st.success(f"✅ PDF processado ({len(texto_pdf.split())} palavras extraídas)")

        # Adiciona contexto ao histórico
        if not any("Este é o conteúdo do PDF" in m["content"] for m in st.session_state.mensagens):
            st.session_state.mensagens.append(
                {"role": "user", "content": f"Este é o conteúdo do PDF:\n{texto_pdf[:15000]}..."}  # Limite de contexto
            )

        # Interface de perguntas
        col1, col2 = st.columns([4, 1])
        with col1:
            pergunta = st.text_input("❓ Faça sua pergunta sobre o PDF", key="pergunta")
        with col2:
            if st.button("📤 Enviar", use_container_width=True):
                if pergunta:
                    st.session_state.mensagens.append({"role": "user", "content": pergunta})
                    
                    with st.spinner("Gerando resposta..."):
                        try:
                            resposta = client.chat.completions.create(
                                messages=st.session_state.mensagens[-6:],  # Mantém apenas 6 últimas mensagens
                                model=model_name,
                                max_tokens=max_tokens,
                                temperature=0.3
                            )
                            resposta_ia = resposta.choices[0].message
                            st.session_state.mensagens.append(resposta_ia.model_dump(exclude_none=True))
                            
                            st.success("💡 Resposta:")
                            st.write(resposta_ia.content)
                            
                        except openai.AuthenticationError:
                            st.error("""
                            🔒 Erro de autenticação:
                            1. Verifique se a chave em Settings > Secrets está correta
                            2. Confira se há créditos disponíveis em https://platform.openai.com/usage
                            """)
                        except openai.RateLimitError:
                            st.error("⚠️ Limite de requisições excedido. Espere um momento ou atualize seu plano.")
                        except Exception as e:
                            st.error(f"Erro inesperado: {str(e)}")
                            st.code(traceback.format_exc(), language="python")

        # Histórico da conversa
        with st.expander("📜 Histórico completo"):
            for msg in st.session_state.mensagens:
                if msg["role"] == "user":
                    st.markdown(f"**👤 Você:** {msg['content'][:200]}...")
                elif msg["role"] == "assistant":
                    st.markdown(f"**🤖 Assistente:** {msg['content'][:200]}...")
                st.divider()

        # Botão de reset
        if st.button("♻️ Limpar Conversa"):
            st.session_state.mensagens = [
                {"role": "system", "content": "Você é um assistente especialista em análise de documentos."},
                {"role": "user", "content": f"Este é o conteúdo do PDF:\n{texto_pdf[:15000]}..."}
            ]
            st.rerun()
            
    else:
        st.warning("Nenhum texto extraído do PDF. Tente outro arquivo.")
else:
    st.info("ℹ️ Envie um PDF para começar a análise.")

# Rodapé
st.caption("🔒 Suas chaves de API nunca são armazenadas ou compartilhadas.")