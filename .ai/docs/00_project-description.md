# Descrição do Projeto: Video UGC Pipeline

## Visão Geral
O Video UGC Pipeline é uma plataforma automatizada para criação de vídeos de marketing gerados por usuários (User-Generated Content - UGC) com base em breves descritivos de campanha. O sistema permite que criadores e marcas desenvolvam rapidamente vídeos promocionais personalizados com mínima intervenção humana.

## Objetivo Principal
Transformar breves descrições textuais de campanhas em vídeos promocionais completos usando inteligência artificial, minimizando o tempo e esforço necessários para produção de conteúdo visual.

## Arquitetura Atual

### Backend (Python/FastAPI)
- API RESTful para gerenciamento de campanhas e vídeos
- Integração com Hugging Face para geração de roteiros de vídeo (LLM)
- Integração com Hugging Face Spaces para geração de vídeo (T2V)
- Integração com Google Drive para armazenamento de vídeos
- Banco de dados SQLite para persistência de metadados
- Worker para processamento assíncrono de jobs

### Frontend (Next.js/React)
- Interface web para criação de campanhas
- Dashboard para monitoramento de jobs de geração de vídeo
- Visualização de status e resultados de processamento
- Integração com API do backend

## Componentes Principais

### 1. Serviço de LLM (Hugging Face)
- Gera roteiros detalhados de vídeo a partir de breves descrições de campanha
- Usa modelos como Meta-Llama-3-8B-Instruct via provedor Hugging Face
- Configurado para usar modelos gratuitos e com baixo custo

### 2. Serviço de Geração de Vídeo (Hugging Face Spaces)
- Usa modelo Wan-AI/Wan2.1-T2V-1.3B via Gradio Client
- Gera vídeos de até 5 segundos com base em prompts textuais
- Implementa estratégia de chamadas sequenciais para extensão de duração
- Usa MoviePy para combinação e transições suaves entre segmentos

### 3. Serviço de Armazenamento (Google Drive)
- Faz upload de vídeos gerados para pasta compartilhada
- Retorna links públicos para compartilhamento
- Integração via Google Drive API

### 4. Pipeline de Processamento
- Estados: PENDING → PROCESSING → COMPLETED/FAILED
- Worker assíncrono verifica jobs pendentes periodicamente
- Processamento paralelo de múltiplos jobs independentes
- Retentativas e tratamento de falhas

## Tecnologias Utilizadas
- **Backend**: Python 3.9+, FastAPI, SQLAlchemy, Hugging Face Hub
- **Frontend**: Next.js 13+, React 18+, TypeScript
- **Banco de Dados**: SQLite
- **IA**: Modelos de linguagem e geração de vídeo do Hugging Face
- **Armazenamento**: Google Drive API
- **Vídeo Processing**: MoviePy, Gradio Client

## Características do Sistema
- **Automatizado**: Produz vídeos com mínima intervenção humana
- **Escalável**: Processamento assíncrono permite alta concorrência
- **Econômico**: Usa modelos gratuitos e APIs com free tier
- **Flexível**: Arquitetura modular permite troca de componentes
- **Monitorável**: Dashboard para acompanhamento de processos

## Limitações Conhecidas
- Tempo de processamento depende de filas do Hugging Face
- Qualidade de vídeo dependente do modelo T2V utilizado
- Limite de duração do vídeo devido a restrições do modelo
- Confiabilidade dependente de serviços externos

## Evolução Futura
- Integração com mais provedores de IA
- Suporte a templates personalizados
- Edição avançada de vídeos
- Integração com redes sociais
- Análise de desempenho de vídeos