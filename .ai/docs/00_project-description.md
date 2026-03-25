# Video_UGC_Pipeline - Descrição do Projeto

## Nome do projeto
Video_UGC_Pipeline

## Objetivo de negócio
Automatizar o fluxo completo de criação de vídeos UGC via código (substituindo ferramentas como n8n), conectando a leitura de um briefing de texto à renderização de vídeo assistida por IA e armazenamento em nuvem.

## Problema principal resolvido
Elimina o tempo operacional de transitar manualmente entre LLMs, geradores de vídeo e drives virtuais, além de automatizar o "polling" e monitoramento de *cold starts* de modelos de vídeo.

## Resultado esperado
Uma solução baseada em Python (FastAPI), com banco de dados SQLite para persistência de status do Job, que permite:
- API/Interface para submissão de briefing
- Integração flexível com diferentes provedores de LLM (Grok da xAI ou Llama 3 via Hugging Face) para gerar scripts/prompts
- Geração de vídeo assistida por IA usando modelos gratuitos do Hugging Face com transições suaves
- Salvamento automatizado no Google Drive
- Front-end simples em Next.js (opcional)

O foco é manter custos zero (Free Tiers) e evitar componentes fora do MVP como edição avançada, lip-sync, deploy cloud de alta disponibilidade e autenticação multi-tenant.

## Público-alvo / Perfis de usuário
- Analistas de Marketing
- Diretores de Arte
- Engenheiros de Automação
- Criadores de Conteúdo (Gestores de Tráfego)

## Stack Tecnológica
- Backend: Python (FastAPI)
- Banco de Dados: SQLite
- Frontend: Next.js (Front-end simples opcional)
- Background Tasks para processamento assíncrono
- APIs externas: xAI Grok (opcional/pago) ou Meta Llama 3 via Hugging Face (gratuito), Hugging Face Spaces para geração de vídeo (gratuita), Google Drive