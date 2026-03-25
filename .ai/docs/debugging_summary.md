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
| `main.py` | Ponto de entrada da aplicação FastAPI, registro de modelos e criação de tabelas |
| `config.py` | Carregamento e validação de variáveis de ambiente |
| `database.py` | Configuração de conexão SQLAlchemy e sessão |
| `api/routes/__init__.py` | Definição de endpoints da API (prefixo `/api`) |
| `api/schemas/` | Modelos Pydantic para validação de requests |
| `api/controllers/` | Lógica de negócio dos endpoints |
| `models/entities/__init__.py` | Modelos SQLAlchemy (Campaign, PipelineJob) |
| `models/pydantic/__init__.py` | Modelos de validação (Campaign, PipelineJob) |
| `services/` | Conectores externos (LLM, Vídeo, Drive) |
| `services/job_service/` | Serviço para inicialização e gerenciamento de jobs |
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

### ✅ [2026-03-24] Troca do modelo LLM de Gemini para Llama 3.1 via Hugging Face
- **Problema:** O modelo original (Google Gemini) era pago e causava dependência de custos
- **Causa:** Necessidade de usar modelos gratuitos para manter custos zero (Free Tiers)
- **Solução:**
  - Substituir Google Generative AI por Hugging Face InferenceClient
  - Configurar token de acesso ao Hugging Face (HF_TOKEN)
  - Atualizar service `services/llm_service/__init__.py` para usar novo cliente
  - Atualizar `.env.example` e `.env` com variáveis do Hugging Face
  - Atualizar `requirements.txt` para incluir dependência `huggingface_hub`

### ✅ [2026-03-24] Frontend recebia erro 422 ao criar campanha
- **Problema:** Erro `422 Unprocessable Entity` ao submeter formulário com briefing
- **Causa:** Proxy API em `pages/api/campaigns.ts` extraía apenas `briefing_text` do request e enviava apenas este campo para o backend, mas o schema Pydantic requer `name` e `briefing_text`
- **Solução:**
  - Alterar `pages/api/campaigns.ts` para extrair ambos os campos: `const { name, briefing_text } = req.body`
  - Validar ambos os campos antes de enviar para o backend
  - Enviar payload completo: `JSON.stringify({ name, briefing_text })`

### ✅ [2026-03-24] Erro "no such table: campaigns" ao criar campanha
- **Problema:** Erro `sqlite3.OperationalError: no such table: campaigns`
- **Causa:** `main.py` estava criando novo `Base` localmente com `declarative_base()`, mas os modelos em `models/entities/__init__.py` herdavam do `Base` do `database.py`. Eram bases diferentes, então as tabelas não eram registradas
- **Solução:**
  - Remover criação local de `Base` e `engine` no `main.py`
  - Importar `Base` e `engine` do `database.py`
  - Importar modelos (`Campaign`, `PipelineJob`) antes de chamar `Base.metadata.create_all()`
  - Arquivo `main.py` agora usa apenas o `Base` compartilhado do `database.py`

### ✅ [2026-03-24] Erro "initialize_new_job is not defined"
- **Problema:** Erro `NameError: name 'initialize_new_job' is not defined` ao criar campanha
- **Causa:** Função `initialize_new_job` não estava importada em `api/routes/__init__.py`
- **Solução:** Adicionar import: `from services.job_service import initialize_new_job`

### ✅ [2026-03-24] Erro "ModuleNotFoundError: No module named 'google.generativeai'"
- **Problema:** Servidor não iniciava por falta do módulo `google-generativeai`
- **Causa:** Pacote não estava listado no `requirements.txt`
- **Solução:**
  - Adicionar `google-generativeai==0.3.2` ao `requirements.txt`
  - Instalar pacote: `pip install google-generativeai==0.3.2`

### ✅ [2026-03-24] Erro na listagem de campanhas "Column expression expected, got []"
- **Problema:** Erro SQLAlchemy ao acessar `/api/campaigns/`
- **Causa:** Query `db.query(campaign.jobs)` é inválida - não se pode fazer query direta de relationship
- **Solução:** Alterar para `db.query(PipelineJob).filter(PipelineJob.campaign_id == campaign.id)`

### ✅ [2026-03-24] Frontend erro "campaigns.map is not a function"
- **Problema:** Erro React ao renderizar lista de campanhas
- **Causa:** Backend retorna `{ data: [...], pagination: {...} }`, mas frontend fazia `setCampaigns(data)` em vez de `setCampaigns(data.data)`
- **Solução:**
  - Alterar `pages/campaigns.tsx` para `setCampaigns(data.data || [])`
  - Adicionar campo `name` na interface `Campaign`
  - Adicionar coluna "Nome" na tabela de campanhas

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

# Listar campanhas
curl http://localhost:8000/api/campaigns/

# Ver detalhes do job
curl http://localhost:8000/api/jobs/1
```

### Debug de Variáveis de Ambiente
```bash
python -c "from config import settings; print(settings.dict())"
```

### Verificar tabelas no banco
```bash
python -c "import sqlite3; conn = sqlite3.connect('video_ugc_pipeline.db'); conn.row_factory = sqlite3.Row; rows = conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall(); print([r[0] for r in rows])"
```

## 5. Novas Soluções Implementadas

### ✅ [2026-03-25] Falha no teste e2e por função ausente get_llm_service
- **Problema:** Erro `ImportError: cannot import name 'get_llm_service' from 'services.llm_service'`
- **Causa:** A função `get_llm_service` era utilizada em `services/job_service/job_service.py` mas não estava definida em `services/llm_service/__init__.py`
- **Solução:**
  - Adicionar função `get_llm_service()` para retornar uma instância singleton do LLMService
  - Certificar que o serviço LLM é inicializado corretamente quando necessário

### ✅ [2026-03-25] Falha no teste de serviços por função ausente test_llm_connection
- **Problema:** Erro `ImportError: cannot import name 'test_llm_connection' from 'services.llm_service'`
- **Causa:** A função `test_llm_connection` era utilizada em `test_services.py` mas não estava definida em `services/llm_service/__init__.py`
- **Solução:**
  - Adicionar função `test_llm_connection()` que encapsula a chamada para o método `test_connection` do LLMService

### ✅ [2026-03-25] Erro de dupla declaração de app FastAPI em main.py
- **Problema:** A aplicação FastAPI era declarada duas vezes em `main.py`, causando conflitos
- **Causa:** Código duplicado durante desenvolvimento resultou em dois objetos `app = FastAPI(...)` na mesma aplicação
- **Solução:**
  - Remover declaração duplicada do objeto FastAPI
  - Manter apenas uma instância e adicionar o lifespan corretamente à única declaração

### ✅ [2026-03-25] Falha no teste e2e por função ausente upload_video_to_drive_and_mark_completed
- **Problema:** Erro `ImportError: cannot import name 'upload_video_to_drive_and_mark_completed'`
- **Causa:** A função era referenciada em `test_e2e.py` mas não existia em `services/job_service/job_service.py`
- **Solução:**
  - Remover import desnecessário da função inexistente
  - Confirmar que a funcionalidade de upload para o Google Drive é coberta por outras funções já existentes
