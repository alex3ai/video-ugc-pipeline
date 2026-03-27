# Estrutura do Banco de Dados

## Entidades

### 1. Campaign (Campanha)
- **Descrição**: Representa uma campanha de marketing para a qual será gerado um vídeo promocional
- **Responsabilidade**: Armazenar informações básicas sobre a campanha e o briefing descritivo

#### Campos
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer (PK) | Identificador único da campanha |
| name | String(255) | Nome da campanha |
| briefing_text | Text | Breve descritivo da campanha para geração do vídeo |
| created_at | DateTime | Timestamp de criação da campanha |
| updated_at | DateTime | Timestamp da última atualização |

#### Relacionamentos
- Um para muitos com PipelineJob (uma campanha pode ter múltiplos jobs de vídeo)

### 2. PipelineJob (Trabalho de Pipeline)
- **Descrição**: Representa uma tarefa individual de geração de vídeo associada a uma campanha
- **Responsabilidade**: Controlar o estado do processo de geração de vídeo, desde a criação até a conclusão

#### Campos
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer (PK) | Identificador único do job |
| campaign_id | Integer (FK) | Referência para a campanha associada |
| status | Enum (JobStatusEnum) | Estado atual do job (PENDING, PROCESSING, COMPLETED, FAILED) |
| prompt | Text | Roteiro gerado para a geração do vídeo |
| video_url | String(500) | URL do vídeo gerado (armazenado no Google Drive) |
| error_message | Text | Mensagem de erro caso o job tenha falhado |
| created_at | DateTime | Timestamp de criação do job |
| updated_at | DateTime | Timestamp da última atualização |

#### Enum: JobStatusEnum
- PENDING: Job aguardando processamento
- PROCESSING: Job em processamento
- COMPLETED: Job concluído com sucesso
- FAILED: Job falhou durante o processamento

#### Relacionamentos
- Muitos para um com Campaign (múltiplos jobs podem pertencer a uma campanha)

## Diagrama de Relacionamento

```
[Campanha] 1 ---- * [PipelineJob]
```

## Considerações de Design

### Normalização
- A estrutura é normalizada para evitar repetição de dados
- A separação entre campanha e job permite múltiplas tentativas de geração para a mesma campanha

### Escalabilidade
- Índices recomendados em campos frequentemente consultados (campaign_id, status)
- Estrutura permite adição de metadados futuros sem impacto significativo

### Persistência
- Usando SQLite para simplicidade e portabilidade
- Estrutura compatível com migração para outros bancos (PostgreSQL, MySQL) se necessário

## Exemplos de Consultas SQL

### Listar campanhas com contagem de jobs
```sql
SELECT c.name, c.briefing_text, COUNT(pj.id) as job_count
FROM Campaign c
LEFT JOIN PipelineJob pj ON c.id = pj.campaign_id
GROUP BY c.id;
```

### Obter jobs pendentes
```sql
SELECT * FROM PipelineJob 
WHERE status = 'PENDING' 
ORDER BY created_at ASC;
```

### Obter status de jobs por campanha
```sql
SELECT c.name, pj.status, pj.created_at
FROM Campaign c
JOIN PipelineJob pj ON c.id = pj.campaign_id
ORDER BY pj.created_at DESC;
```