# Estrutura de Banco de Dados - Video_UGC_Pipeline

Este documento descreve a estrutura do banco de dados SQLite para o projeto Video_UGC_Pipeline.

## Entidade: Campaign
Armazena as informações básicas das campanhas submetidas ao sistema.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID (PK) | Identificador único da campanha |
| name | String | Nome da campanha (obrigatório) |
| briefing_text | Text | Texto do briefing da campanha (obrigatório, mínimo 50, máximo 2000 caracteres) |
| created_at | Datetime | Data e hora de criação da campanha |

## Entidade: PipelineJob
Registra os trabalhos de processamento da pipeline de vídeo, incluindo status e resultados.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID (PK) | Identificador único do job |
| campaign_id | UUID (FK -> Campaign.id) | Chave estrangeira referenciando a campanha associada |
| status | Enum | Status do job (PENDING, PROMPT_GENERATED, PROCESSING_VIDEO, COMPLETED, FAILED, TIMEOUT) |
| generated_prompt | Text (Nullable) | Prompt gerado pelo sistema (opcional) |
| video_url | String (Nullable) | Link final do vídeo no Google Drive (opcional) |
| error_log | Text (Nullable) | Registro de erros ocorridos durante o processamento (opcional) |
| created_at | Datetime | Data e hora de criação do job |
| updated_at | Datetime | Data e hora da última atualização do job |

## Relacionamentos
- Um Campaign pode ter um ou mais PipelineJob
- Um PipelineJob pertence a um único Campaign

## Restrições e Considerações
- O sistema deve estabelecer concorrência máxima de processamento de 1 job por vez, baseando-se nos status PENDING ou em andamento.
- Os campos briefing_text têm limites de tamanho entre 50 e 2000 caracteres.
- Os campos created_at e updated_at devem ser gerenciados automaticamente pelo sistema.