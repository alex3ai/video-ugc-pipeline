# 01_user-stories

## Instrução de uso
Com base em .ai/docs/00_project-description.md, gere user stories no formato abaixo sem inventar funcionalidades fora do escopo explícito.

- [x] Como [PERFIL], quero [AÇÃO], para [VALOR].
  Critérios:
  - Dado [contexto], quando [ação], então [resultado]
  - Regra de negócio: [descreva regra concreta]
  - Edge case: [inclua pelo menos um]

## Regras obrigatórias
1. Não inventar funcionalidades fora do escopo EXPLÍCITO ✅.
2. Incluir pelo menos 1 edge case por user story.
3. Para ambiguidades, listar perguntas em aberto ao final.

## User Stories

### US01 - Submissão de Briefing
- [x] Como usuário, quero inserir o texto da minha campanha para que o sistema registre a solicitação na fila de processamento e inicie a pipeline autonomamente.
  Critérios:
  - Dado que o usuário deseja criar um vídeo com base em um briefing textual, quando o usuário envia o briefing via API, então o sistema deve registrar a solicitação e iniciar a pipeline
  - Regra de negócio: O sistema deve validar o formato do briefing antes de aceitá-lo
  - Edge case: Se o briefing for muito longo ou em formato inválido, o sistema deve retornar erro

### US02 - Geração de Prompt (Automático)
- [x] Como sistema, preciso ler o briefing no banco, acionar a API do Gemini pedindo a criação de um "prompt visual em inglês" e salvar o resultado no job. Em caso de falha da API, tentar novamente até 3 vezes.
  Critérios:
  - Dado que existe um job com briefing válido no banco de dados, quando o sistema detecta um job pendente, então deve acionar a API do Gemini para gerar o prompt
  - Regra de negócio: O sistema deve limitar a 3 tentativas consecutivas em caso de falha na API
  - Edge case: Se a API do Gemini retornar conteúdo inadequado, o sistema deve marcar o job para revisão humana

### US03 - Renderização de Vídeo (Automático)
- [x] Como sistema, preciso enviar o prompt para a API de Vídeo e entrar em um loop de verificação inteligente (tratando respostas 503 e estimativas de tempo) até receber o vídeo completo ou atingir timeout de 10 min.
  Critérios:
  - Dado que existe um prompt visual gerado, quando o sistema envia o prompt para a API de vídeo, então deve iniciar o processo de renderização com polling inteligente
  - Regra de negócio: O sistema deve implementar backoff exponencial nas requisições de polling
  - Edge case: Se a API de vídeo retornar erro 503 repetidamente por 10 vezes, o sistema deve cancelar o job

### US04 - Entrega (Automático)
- [x] Como sistema, ao obter os bytes do vídeo final, devo fazer upload direto para o Google Drive configurado e atualizar o job para `COMPLETED`.
  Critérios:
  - Dado que o vídeo foi gerado com sucesso, quando o sistema recebe os bytes do vídeo, então deve fazer upload para o Google Drive e atualizar o status
  - Regra de negócio: O sistema deve usar credenciais OAuth2 para autenticação no Google Drive
  - Edge case: Se o upload para o Google Drive falhar após 3 tentativas, o sistema deve manter o vídeo em storage temporária

### US05 - Acompanhamento
- [x] Como usuário, quero visualizar uma lista de campanhas e o status em tempo real de cada etapa (Pendente, Gerando Prompt, Renderizando, Concluído) para saber quando o vídeo está pronto.
  Critérios:
  - Dado que existem jobs em diferentes estágios, quando o usuário acessa a interface de acompanhamento, então deve ver o status atualizado de todos os jobs
  - Regra de negócio: O sistema deve permitir filtragem por status e data
  - Edge case: Se o usuário tentar acessar detalhes de um job inexistente, o sistema deve retornar erro 404

## [PERGUNTAS EM ABERTO]
- [ ] Como será implementada a autenticação para a API de submissão de briefing?
- [ ] Qual é o formato exato do briefing que o sistema deve aceitar?
- [ ] Como será tratada a atualização de jobs já existentes no sistema?
- [ ] Quais são os requisitos específicos para armazenamento de dados (banco de dados)?
- [ ] Como será implementada a notificação ao usuário quando o vídeo estiver pronto?
