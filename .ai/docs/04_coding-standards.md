# Padrões de Codificação

## Python

### Geral
- Use snake_case para nomes de funções e variáveis
- Use PascalCase para classes
- Use constante MAIÚSCULAS para constantes globais
- Use Type Hints em todas as funções públicas

### Assíncrono
- Use `async def` para funções que fazem operações assíncronas
- Use `await` para aguardar operações assíncronas
- Ao chamar funções assíncronas de código síncrono, use `asyncio.run()`

### Serviços
- Implemente serviços como classes com métodos bem definidos
- Use injeção de dependência via construtor ou parâmetros
- Evite estado global quando possível
- Use padrão Singleton para serviços que não precisam de estado diferenciado

### Tratamento de Erros
- Use try/except para capturar erros esperados
- Registre erros inesperados com logging
- Evite capturar exceções genéricas desnecessariamente
- Implemente fallbacks para serviços externos quando possível

## JavaScript/TypeScript

### Geral
- Use camelCase para nomes de funções e variáveis
- Use PascalCase para classes e interfaces
- Use Type Hints em todas as funções públicas (TypeScript)
- Prefira arrow functions para callbacks simples

### API Calls
- Use try/catch para tratamento de erros em requisições
- Implemente timeouts apropriados para chamadas externas
- Trate erros de rede e de resposta da API de forma distinta
- Use mensagens de erro claras para o usuário final

## Documentação

### Commits
- Use Conventional Commits (feat:, fix:, refactor:, etc.)
- Descreva claramente o problema resolvido
- Referencie issues quando aplicável

### Código
- Documente funções públicas com docstrings
- Use comentários para explicar decisões complexas
- Evite comentários óbvios
- Mantenha a documentação sincronizada com o código
