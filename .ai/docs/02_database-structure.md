# 02_database-structure

## Resumo Conceitual
Para cada entidade principal:
- Entidade:
- Propósito:
- Regras de negócio críticas:
  - 
- Relacionamentos:
  - 

## Especificação Técnica
### [Nome da Entidade]
| Campo | Tipo | Restrições | Observações |
|-------|------|------------|-------------|
| id | UUID | PK, obrigatório | Gerado automaticamente |
| created_at | TIMESTAMPTZ | DEFAULT now() | Audit trail |
| updated_at | TIMESTAMPTZ | DEFAULT now() | Última atualização |
| status | ENUM | DEFAULT 'active' | Ajustar aos valores do domínio |

## Edge Cases Documentados
- [ ] Cenário:
- [ ] Ação esperada:

## Regras obrigatórias
1. Sempre incluir campos padrão quando fizer sentido.
2. Para cada campo das user stories, confirmar existência de coluna ou estrutura correspondente.
3. Para dados não relacionais, documentar em seção específica.
4. Nunca inventar campos fora do escopo documentado em 00_project-description.md.
