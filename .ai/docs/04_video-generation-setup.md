# Setup da Geração de Vídeo

## Visão Geral
Este documento detalha como configurar e usar a nova abordagem de geração de vídeo baseada em modelos gratuitos do Hugging Face.

## Requisitos

### Dependências Python
```bash
pip install gradio-client moviepy python-dotenv pydantic-settings requests torch transformers
```

### Conta no Hugging Face
1. Crie uma conta em [https://huggingface.co/join](https://huggingface.co/join)
2. Gere um token de acesso em [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
3. Aceite os termos de uso para os modelos que serão utilizados:
   - [Wan-AI/Wan2.1-T2V-1.3B](https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B)
   - [ali-vilab/modelscope-text-to-video-synthesis](https://huggingface.co/ali-vilab/modelscope-text-to-video-synthesis)

## Configuração

### Variáveis de Ambiente
Adicione as seguintes variáveis ao seu arquivo [.env](file:///c%3A/Users/alex_%5CDesktop%5CPE33%5CProjetos%20PE33%5CProjeto%2021%20-%20Video%20UGC%20Pipeline%5CVideo_UGC_Pipeline/.env):

```env
# Token de acesso ao Hugging Face
HF_API_KEY=sua_chave_de_acesso

# Modelo do Hugging Face Space para geração de vídeo
HF_SPACE_MODEL=Wan-AI/Wan2.1-T2V-1.3B

# Duração de cada segmento de vídeo em segundos
VIDEO_DURATION_PER_SEGMENT=5

# Duração da transição em segundos
CROSSFADE_DURATION=1.0

# Diretório temporário para processamento de vídeos
TEMP_VIDEO_DIR=/tmp

# Caminho para credenciais do Google Drive
GOOGLE_CREDENTIALS_PATH=caminho_para_suas_credenciais.json

# ID da pasta no Google Drive para salvar os vídeos
GOOGLE_DRIVE_FOLDER_ID=id_da_sua_pasta_no_drive
```

## Funcionamento

### Processo de Geração de Vídeo
1. O sistema faz uma chamada para o modelo T2V com o prompt fornecido para gerar um vídeo de 5 segundos
2. Uma segunda chamada idêntica é feita para gerar outro vídeo de 5 segundos com o mesmo prompt
3. Os dois vídeos são combinados usando a biblioteca MoviePy
4. É aplicada uma transição de crossfade de 1 segundo entre os vídeos
5. O vídeo final de ~10 segundos é salvo como `video_final_10s.mp4`

### Código de Exemplo

```python
from services.video_service.video_service import generate_video_from_prompt

# Exemplo de uso
prompt = "Uma paisagem montanhosa com lago e pôr do sol"
result = generate_video_from_prompt(prompt, campaign_id=123)

if result['status'] == 'success':
    print(f"Vídeo gerado com sucesso: {result['video_path']}")
else:
    print(f"Erro na geração do vídeo: {result['error']}")
```

## Tratamento de Erros

A implementação inclui tratamento para:

- Filas no Hugging Face: Aguarda automaticamente até que o modelo esteja disponível
- Falhas de conexão: Tenta novamente com backoff exponencial
- Erros de processamento de vídeo: Retorna mensagens de erro descritivas
- Limite de uso: Respeita os limites de uso dos modelos gratuitos

## Melhorias Futuras

- Implementar cache de vídeos gerados para evitar repetições
- Adicionar opção de escolha entre diferentes modelos T2V
- Permitir personalização avançada de parâmetros de vídeo
- Adicionar suporte para outros tipos de transições