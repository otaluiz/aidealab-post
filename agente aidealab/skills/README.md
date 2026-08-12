# Skills — Agência aidealab

Skills de automação da aidealab (agência de conteúdo Instagram). Cada pasta é
uma Agent Skill (`SKILL.md`), usando as ferramentas MCP já conectadas à conta
(Google Drive, e as que forem entrando conforme as próximas skills forem
desenhadas).

## Catálogo

| Skill | Dispara por fala? | Papel |
|---|---|---|
| `criar-cliente` | sim | garante a estrutura padrão de pastas do cliente no Drive |

Planejadas, cada uma com spec própria em `docs/superpowers/specs/` antes de
virar skill (ainda não criadas): **criar carrossel**, **postar no Instagram**,
**criar site**. Todas dependem de `criar-cliente` para localizar a pasta certa
do cliente.

## Convenções

- Uma pasta por skill, `SKILL.md` (+ `references/*.md` quando a skill precisar
  de código ou tabela de apoio).
- Skill descreve só instrução — sem script externo. As chamadas MCP citadas no
  `SKILL.md` são as ferramentas reais já conectadas à conta, não aliases (ao
  contrário do agente de processo, aqui não há necessidade de indireção porque
  não há reexportação para outro ambiente).
