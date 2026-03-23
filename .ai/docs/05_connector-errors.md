# Erros Comuns dos Conectores

## LLM Service (Google Gemini)

### Erro: `API key not valid`
- **Causa:** Chave de API ausente, expirada ou inválida
- **Solução:** 
  1. Verificar se `GEMINI_API_KEY` está definida no `.env`
  2. Validar chave no [Google AI Studio](https://makersuite.google.com/app/apikey)
  3. Renovar chave se expirada

### Erro: `400 API key not valid. Please pass a valid API key`
- **Causa:** Formato da chave incorreto ou permissões insuficientes
- **Solução:** 
  1. Remover espaços em branco ao copiar a chave
  2. Verificar se a API Gemini está habilitada no projeto Google Cloud

### Erro: `models/gemini-pro is not found for API version v1beta`
- **Causa:** Modelo indisponível ou versão de API desatualizada
- **Solução:** 
  1. Usar `gemini-1.5-flash` ou `gemini-1.5-pro` como alternativa
  2. Atualizar pacote `google-generativeai` para versão mais recente

### Erro: `Environment variable GOOGLE_API_USE_CLIENT_CERTIFICATE must be either true or false`
- **Causa:** Variável de ambiente não definida ou com valor inválido
- **Solução:** Adicionar ao `.env`: `GOOGLE_API_USE_CLIENT_CERTIFICATE=false`

---

## Video Service (API de Vídeo)

### Erro: `401 Unauthorized`
- **Causa:** Chave de API inválida ou ausente no header
- **Solução:** 
  1. Verificar `VIDEO_API_KEY` no `.env`
  2. Confirmar formato do header `Authorization: Bearer {api_key}`

### Erro: `403 Forbidden`
- **Causa:** API key válida mas sem permissões para o endpoint
- **Solução:** 
  1. Verificar escopos/permissões da chave no dashboard da API
  2. Confirmar se o plano atual permite acesso ao endpoint

### Erro: `503 Service Unavailable (Cold Start)`
- **Causa:** API em inicialização ou sobrecarregada
- **Solução:** 
  1. Implementar retry com backoff exponencial (já previsto no `config.py`)
  2. Aguardar 30-60 segundos antes de retentar

### Erro: `Connection timeout`
- **Causa:** URL inválida ou serviço indisponível
- **Solução:** 
  1. Verificar `VIDEO_API_URL` no `.env`
  2. Testar conectividade com `curl {VIDEO_API_URL}/test`
  3. Ajustar `REQUEST_TIMEOUT` no `.env` se necessário

---

## Drive Service (Google Drive)

### Erro: `google.auth.exceptions.DefaultCredentialsError`
- **Causa:** Arquivo de credenciais não encontrado ou inválido
- **Solução:** 
  1. Verificar se `GOOGLE_CREDENTIALS_PATH` aponta para arquivo válido
  2. Confirmar formato JSON das credenciais de service account
  3. Baixar novo arquivo de credenciais no [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

### Erro: `insufficientPermissions`
- **Causa:** Service account sem acesso à pasta do Drive
- **Solução:** 
  1. Compartilhar a pasta do Drive com o email do service account
  2. Verificar se `GOOGLE_DRIVE_FOLDER_ID` está correto
  3. Conceder permissão de "Editor" para o service account

### Erro: `File not found: {file_id}`
- **Causa:** ID do arquivo/pasta incorreto ou arquivo deletado
- **Solução:** 
  1. Verificar ID no URL do Drive (parte após `/folders/`)
  2. Confirmar que o arquivo ainda existe no Drive

### Erro: `Quota exceeded`
- **Causa:** Limite de requisições da API atingido
- **Solução:** 
  1. Implementar rate limiting nas requisições
  2. Aguardar reset do quota (geralmente 100 segundos)
  3. Solicitar aumento de quota no Google Cloud Console

---

## Debugging Geral

### Verificar variáveis de ambiente
```bash
python -c "from config import settings; print(settings.dict())"
```

### Testar conexões individualmente
```bash
python -c "from services.llm_service import test_gemini_connection; print(test_gemini_connection())"
python -c "from services.video_service import test_video_api_connection; print(test_video_api_connection())"
python -c "from services.drive_service import test_drive_connection; print(test_drive_connection())"
```

### Rodar testes unitários
```bash
python test_services.py -v
```
