# Erros Comuns e Soluções - Conectores

## LLM Service (Grok ou Hugging Face Llama)

### Erros de API Key
- **Erro**: `Invalid API key`
- **Solução**: Verifique se as variáveis de ambiente `GROK_API_KEY`, `LLAMA_API_KEY` ou `HF_API_KEY` estão corretamente configuradas

### Erros de Conexão
- **Erro**: `Connection timeout` ou `Network error`
- **Solução**: Verifique sua conexão com a internet e os limites de taxa da API

## Video Service (Hugging Face Spaces - Nova Abordagem)

### Erros de Conexão com o Hugging Face Space
- **Erro**: `Connection error` ao acessar o modelo T2V
- **Solução**: Verifique se o modelo está disponível no Hugging Face Space e se você aceitou os termos de uso

### Erros de Fila no Hugging Face
- **Erro**: `Queue timeout` ou `Model is currently loading`
- **Solução**: Espere alguns minutos e tente novamente, ou selecione um modelo diferente em `HF_SPACE_MODEL`

### Erros de Processamento de Vídeo
- **Erro**: `MoviePy error` durante combinação de vídeos
- **Solução**: Verifique se o FFmpeg está instalado e disponível no PATH do sistema

### Erros de Dependências
- **Erro**: `ModuleNotFoundError` para `gradio_client` ou `moviepy`
- **Solução**: Execute `pip install -r requirements.txt` para instalar as dependências

## Drive Service (Google Drive)

### Erros de Credenciais
- **Erro**: `Invalid credentials` ou `Credentials file not found`
- **Solução**: Verifique se `GOOGLE_CREDENTIALS_PATH` aponta para o arquivo JSON de credenciais válido

### Erros de Permissão
- **Erro**: `Insufficient permissions`
- **Solução**: Certifique-se de que a conta de serviço tem permissões de escrita na pasta especificada

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
