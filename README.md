# Video UGC Pipeline

Uma plataforma automatizada para criação de vídeos de marketing gerados por usuários (User-Generated Content - UGC) com base em breves descrições de campanha. O sistema transforma inputs textuais em vídeos promocionais completos usando inteligência artificial.

## 🚀 Funcionalidades

- **Criação Automatizada**: Transforma breves descrições textuais em vídeos promocionais
- **Integração com IA**: Utiliza modelos avançados de linguagem e geração de vídeo
- **Processamento Assíncrono**: Jobs de geração de vídeo processados em background
- **Armazenamento na Nuvem**: Vídeos gerados armazenados no Google Drive
- **Interface Web**: Dashboard intuitivo para criação e monitoramento de campanhas

## 🛠️ Tecnologias

- **Backend**: Python 3.9+ com FastAPI
- **Frontend**: Next.js 13+ com React 18+
- **Banco de Dados**: SQLite com SQLAlchemy
- **IA**: Modelos Hugging Face (LLM e T2V)
- **Vídeo**: MoviePy e Gradio Client
- **Armazenamento**: Google Drive API

## 📋 Pré-requisitos

- Python 3.9+
- Node.js 16+
- Conta no Hugging Face com acesso à API
- Conta no Google com acesso ao Google Drive API

## 🚀 Instalação

### Backend

1. Clone o repositório:
```bash
git clone <repository-url>
cd Video_UGC_Pipeline
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

5. Inicie o servidor:
```bash
python start_app.py
```

### Frontend

1. Navegue até o diretório do frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Configure as variáveis de ambiente:
```bash
cp .env.local.example .env.local
# Edite .env.local com suas configurações
```

4. Inicie o servidor de desenvolvimento:
```bash
npm run dev
```

## ⚙️ Configuração

O sistema requer as seguintes configurações:

### Hugging Face
- `HF_API_KEY` ou `HF_TOKEN`: Token de acesso à API do Hugging Face
- `HF_MODEL`: Modelo de LLM a ser utilizado (padrão: `meta-llama/Meta-Llama-3-8B-Instruct`)
- `HF_PROVIDER`: Provedor de inferência (padrão: `huggingface`)
- `HF_SPACE_MODEL`: Modelo de geração de vídeo (padrão: `AlexMendes33/Wan-AI-Wan2.1-T2V-1.3B`)

### Google Drive
- `GOOGLE_CREDENTIALS_PATH`: Caminho para o arquivo de credenciais do Google
- `GOOGLE_DRIVE_FOLDER_ID`: ID da pasta do Google Drive para armazenamento

## 🎯 Uso

Para executar o pipeline de geração de vídeo:

1. Certifique-se de ter as credenciais configuradas corretamente
2. Execute o backend com `python start_app.py`
3. Envie uma requisição POST para `/api/campaigns/` com os detalhes da campanha
4. O sistema processará a solicitação e gerará um vídeo promocional

## 🔧 Solução de Problemas

Se encontrar problemas com a geração de vídeo:

1. Verifique se o token do Hugging Face está configurado corretamente
2. Confirme que o modelo de vídeo especificado em `HF_SPACE_MODEL` está acessível
3. Execute `python test_video_connection.py` para verificar a conexão com o provedor de vídeo

## 🤖 Agentes

O sistema utiliza agentes especializados para diferentes tarefas:

- **Script Generator Agent**: Responsável por criar roteiros criativos com base nas informações da campanha
- **Video Generator Agent**: Processa os roteiros e gera os vídeos promocionais
- **Upload Agent**: Faz upload dos vídeos gerados para o Google Drive

Mais informações sobre os agentes podem ser encontradas no arquivo [AGENTS.md](AGENTS.md).

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.