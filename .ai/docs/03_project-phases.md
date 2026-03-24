03_project-phases.md
# Fases do Projeto - Video_UGC_Pipeline

## Fase 0: Foundation e Conectores
Esta fase estabelece a base técnica do projeto com setup inicial e módulos de serviço isolados.

### Tarefas pequenas:
- [x] Configurar ambiente Python com FastAPI e SQLAlchemy
- [x] Criar estrutura básica de diretórios do projeto
- [x] Configurar banco de dados SQLite com conexão funcional
- [x] Criar módulo `llm_service.py` com função de teste para conexão com Gemini
- [x] Criar módulo `video_service.py` com função de teste para conexão com API de vídeo
- [x] Criar módulo `drive_service.py` com função de teste para conexão com Google Drive
- [x] Implementar configuração de variáveis de ambiente para chaves de API
- [x] Realizar testes unitários básicos para cada módulo de serviço
- [x] Documentar erros comuns e soluções para cada conector

## Fase 1: Pipeline Core (Worker/Background Task)
Esta fase implementa a lógica central do processamento automatizado da pipeline.

### Tarefas pequenas:
- [x] Criar modelo Pydantic para `Campaign` com validação de briefing_text (50-2000 chars)
- [x] Criar modelo Pydantic para `PipelineJob` com enumeração de status
- [x] Criar modelos SQLAlchemy para persistência no banco de dados
- [x] Implementar função de inicialização de novo job com status PENDING
- [x] Implementar worker para buscar jobs PENDING no banco
- [x] Integrar `llm_service.py` com a geração de prompt para jobs PENDING
- [x] Implementar lógica de retry (até 3 vezes) para falhas na API do Gemini
- [x] Implementar função de transição de status PENDING -> PROMPT_GENERATED
- [x] Implementar função de envio do prompt para API de vídeo
- [x] Implementar lógica de polling inteligente com backoff exponencial para status PROCESSING_VIDEO
- [x] Tratar respostas HTTP 503 (Cold Start) com retentativa
- [x] Implementar timeout de 10 minutos para o processo de renderização
- [x] Implementar transição de status PROCESSING_VIDEO -> COMPLETED
- [x] Implementar transições para status FAILED e TIMEOUT com logs de erro
- [x] Garantir restrição de execução de apenas 1 job por vez
- [x] Testar máquina de estados completa com diferentes cenários

## Fase 2: Front-end e Entrega final
Esta fase implementa a interface com o usuário e finaliza a pipeline completa.

### Tarefas pequenas:
- [x] Criar endpoint POST para submissão de nova campanha
- [x] Implementar validação do briefing_text no endpoint de submissão
- [x] Criar endpoint GET para listagem de campanhas e seus jobs
- [x] Implementar filtro por status no endpoint de listagem
- [x] Criar endpoint GET para detalhes de um job específico
- [x] Implementar paginação para listagens grandes
- [x] Desenvolver front-end simples em Next.js com formulário de submissão
- [x] Implementar dashboard com listagem de campanhas e status em tempo real
- [x] Integrar `drive_service.py` com upload do vídeo gerado para Google Drive
- [x] Implementar persistência do link do vídeo no campo video_url do job
- [x] Implementar atualização de status para COMPLETED após upload no Drive
- [x] Adicionar tratamento de falhas no upload para Google Drive (3 tentativas)
- [ ] Implementar armazenamento temporário em caso de falha de upload
- [ ] Testar fluxo completo: briefing → prompt → vídeo → upload → link
- [ ] Realizar testes de ponta a ponta para validação final
- [ ] Documentar a API com exemplos de uso