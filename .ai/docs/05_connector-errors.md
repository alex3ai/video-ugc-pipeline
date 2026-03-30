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

### Erros de Integração com Hugging Face Hub
- **Erro**: `404 Client Error`, `Repository Not Found` ou `Space não acessível`
- **Causa**: Nome do repositório incorreto ou tipo de repositório errado (usando `repo_type="model"` em vez de `repo_type="space"`)
- **Solução**: 
  1. Verifique se o `HF_SPACE_MODEL` está configurado corretamente com o nome completo do repositório (ex: `AlexMendes33/Wan-AI-Wan2.1-T2V-1.3B`)
  2. Confirme que o tipo de repositório está correto como "space" e não "model"
  3. Execute `python test_video_connection.py` para verificar a conectividade

### Erros de Autenticação com Hugging Face
- **Erro**: Mensagem de aviso `"HF_TOKEN is set and is the current active token independently from the token you've just configured"`
- **Causa**: Chamada redundante à função `huggingface_hub.login()` quando o token já está configurado como variável de ambiente
- **Solução**: Remover chamadas manuais de login quando o token já está disponível como variável de ambiente

### Erros com o Cliente Gradio
- **Erro**: `Client.__init__() got an unexpected keyword argument 'hf_token'`
- **Causa**: Uso do parâmetro errado ao inicializar o cliente Gradio
- **Solução**: Use o parâmetro `token` ao invés de `hf_token` ao inicializar o cliente: `Client(repo_id, token=hf_token)`

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

### Testar a integração de vídeo específica
```bash
python test_video_connection.py
```