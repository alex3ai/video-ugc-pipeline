# 🤖 Memória de Longo Prazo do Projeto

> Regra: descreva lógica, não cole código. Mantenha objetivo.

## 1. Stack e Arquitetura
- **Backend:** Python 3.x + FastAPI
- **Banco de Dados:** SQLite (via SQLAlchemy 2.0)
- **Frontend:** Next.js 13 + React 18 + TypeScript
- **APIs Externas:** Google Gemini, API de Vídeo (Hugging Face ou similar), Google Drive
- **Gerenciamento de Ambiente:** python-dotenv + pydantic-settings
- **Servidor:** Uvicorn (ASGI)

## 2. Mapa de Arquivos (Responsabilidades)

### Backend
| Arquivo | Responsabilidade |
|---------|------------------|
| `main.py` | Ponto de entrada da aplicação FastAPI |
| `config.py` | Carregamento e validação de variáveis de ambiente |
| `database.py` | Configuração de conexão SQLAlchemy e sessão |
| `api/routes/__init__.py` | Definição de endpoints da API (prefixo `/api`) |
| `api/schemas/` | Modelos Pydantic para validação de requests |
| `api/controllers/` | Lógica de negócio dos endpoints |
| `models/entities/__init__.py` | Modelos SQLAlchemy (Campaign, PipelineJob) |
| `models/pydantic/__init__.py` | Modelos de validação (Campaign, PipelineJob) |
| `services/` | Conectores externos (LLM, Vídeo, Drive) |
| `utils/` | Funções utilitárias e helpers |

### Frontend
| Arquivo | Responsabilidade |
|---------|------------------|
| `pages/index.tsx` | Formulário de submissão de campanha |
| `pages/campaigns.tsx` | Listagem de campanhas e jobs |
| `pages/api/campaigns.ts` | Proxy API para criar campanha (POST) |
| `pages/api/campaigns-list.ts` | Proxy API para listar campanhas (GET) |
| `components/Header.tsx` | Cabeçalho compartilhado |

### Configuração
| Arquivo | Responsabilidade |
|---------|------------------|
| `.env` | Variáveis de ambiente (não versionado) |
| `.env.example` | Template de variáveis de ambiente |
| `requirements.txt` | Dependências Python |
| `frontend/package.json` | Dependências Node.js |

## 3. Log de Soluções

### ✅ [2026-03-23] Variáveis de ambiente não carregavam
- **Problema:** Erro `Erros de configuração encontrados: GEMINI_API_KEY não está definida` mesmo com `.env` criado
- **Causa:** `pydantic-settings` não carregava automaticamente o arquivo `.env`
- **Solução:** 
  - Adicionar `from dotenv import load_dotenv` e `load_dotenv()` no início do `config.py`
  - Adicionar `python-dotenv==1.0.0` e `pydantic-settings==2.1.0` no `requirements.txt`

### ✅ [2026-03-23] Rotas da API retornavam 404
- **Problema:** Frontend chamava `/campaigns` mas backend registrava `/api/v1/campaigns/`
- **Causa:** Prefixo das rotas inconsistente entre backend e frontend
- **Solução:** 
  - Alterar prefixo em `api/routes/__init__.py` de `/api/v1` para `/api`
  - Atualizar frontend para chamar `/api/campaigns/` (com slash final)

### ✅ [2026-03-23] Validação de schema falhava ao criar campanha
- **Problema:** Erro 400 - campo `name` obrigatório faltando
- **Causa:** Modelo Pydantic `Campaign` requer `name`, mas frontend enviava apenas `briefing_text`
- **Solução:** 
  - Adicionar campo "Nome da Campanha" no formulário (`pages/index.tsx`)
  - Incluir `name` no payload enviado para API

### ✅ [2026-03-23] Servidor não respondia na porta 8000
- **Problema:** `python main.py` iniciava mas não servia requisições
- **Causa:** `main.py` apenas define a app FastAPI, não inicia o servidor
- **Solução:** Usar `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

### ⚠️ [2026-03-23] Aviso de depreciação do SQLAlchemy
- **Problema:** `MovedIn20Warning: declarative_base() is now available as sqlalchemy.orm.declarative_base()`
- **Status:** Aviso não crítico, pode ser corrigido futuramente migrando import no `main.py`

## 4. Comandos Úteis

### Iniciar Backend
```bash
# Ativar venv
.\venv\Scripts\Activate.ps1

# Iniciar servidor (com auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Iniciar Frontend
```bash
cd frontend
npm install  # primeira vez
npm run dev
```

### Testar API
```bash
# Endpoint raiz
curl http://localhost:8000

# Swagger UI
http://localhost:8000/docs
```

### Debug de Variáveis de Ambiente
```bash
python -c "from config import settings; print(settings.dict())"
```
