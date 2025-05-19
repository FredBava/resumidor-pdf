# 📄🔍 Analisador de PDF com IA

Este é um aplicativo web simples, desenvolvido com Python e Streamlit, que permite ao usuário fazer perguntas sobre o conteúdo de um arquivo PDF usando a API da OpenAI (GPT-4o).

---

## 🚀 Funcionalidades

- Upload de arquivos PDF.
- Extração automática de texto do PDF.
- Geração de respostas com base no conteúdo do documento usando GPT.
- Histórico de conversas armazenado durante a sessão.

---

## 🛠️ Tecnologias utilizadas

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [OpenAI API](https://platform.openai.com/)
- [PyPDF2](https://pypi.org/project/PyPDF2/)
- [dotenv](https://pypi.org/project/python-dotenv/)

---

## 📦 Instalação

1. **Clone o repositório:**

git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio

Crie e configure o arquivo .env:

Crie um arquivo .env baseado no .env.example e adicione sua chave da OpenAI:

OPENAI_API_KEY=sua-chave-aqui

Instale as dependências:

pip install -r requirements.txt
Execute o aplicativo:

streamlit run app.py
