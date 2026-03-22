# Padrões de Código e Comportamento

## Comunicação
- Responder em português no chat.
- Mensagens de commit somente em inglês.
- Usar Conventional Commits: feat:, fix:, chore:, refactor:, docs:, test:.

## Infraestrutura
- Foco em mínima infraestrutura viável.
- Priorizar Docker Compose sobre Kubernetes para MVPs, salvo exigência explícita.
- Evitar serviços gerenciados caros quando container resolver.

## Documentação
- A cada alteração, atualizar .ai/docs quando necessário.
- Docstrings obrigatórias para funções públicas.
- Atualizar debugging_summary.md com: [Status] Problema → Solução.

## Validação
- Antes de codificar: comparar specs vs código e listar discrepâncias.
- Após codificar: realizar testes compatíveis com a alteração.
- Antes de concluir: revisar se a entrega respeita o escopo explícito.
