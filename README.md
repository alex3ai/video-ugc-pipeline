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
uvicorn main:app --reload --host 0.0.0.0 --port 8000
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
- `HF_API_KEY`: Token de acesso à API do Hugging Face
- `HF_MODEL`: Modelo de LLM a ser utilizado (padrão: `meta-llama/Meta-Llama-3-8B-Instruct`)
- `HF_PROVIDER`: Provedor de inferência (padrão: `huggingface`)
- `HF_SPACE_MODEL`: Modelo de geração de vídeo (padrão: `Wan-AI/Wan2.1-T2V-1.3B`)

### Google Drive
- `GOOGLE_CREDENTIALS_PATH`: Caminho para o arquivo de credenciais do Google
- `GOOGLE_DRIVE_FOLDER_ID`: ID da pasta do Google Drive para armazenamento

## 🎯 Uso

1. Acesse o dashboard em `http://localhost:3000`
2. Crie uma nova campanha informando nome e descrição
3. Aguarde o processamento do vídeo (monitore o status na página de campanhas)
4. Acesse o vídeo gerado através do link disponibilizado

## 🔧 Arquitetura

### Backend
- `main.py`: Ponto de entrada da aplicação FastAPI
- `config.py`: Configurações e variáveis de ambiente
- `database.py`: Configuração do banco de dados
- `models/`: Modelos ORM e Pydantic
- `api/routes/`: Endpoints da API
- `services/`: Serviços de integração (LLM, Vídeo, Drive)
- `worker.py`: Processamento assíncrono de jobs

### Frontend
- `pages/`: Páginas da aplicação Next.js
- `components/`: Componentes reutilizáveis
- `public/`: Recursos estáticos

## 🧪 Testes

Execute os testes com:
```bash
# Backend
python -m pytest

# Frontend
npm run test
```

## 🤝 Contribuindo

Contribuições são o que tornam a comunidade open source um lugar incrível para aprender, inspirar e criar. Qualquer contribuição que você fizer será muito apreciada.

1. Faça um fork do projeto
2. Crie um branch com sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit de suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para o branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 👨‍💻 Autor

- Alex Oliveira Mendes - Desenvolvedor Principal

Projeto criado para demonstrar a aplicação de tecnologias modernas na automação de criação de conteúdo de vídeo.
