# Skills — Agência aidealab

Skills de automação da aidealab (agência de conteúdo Instagram). Cada pasta é
uma Agent Skill (`SKILL.md`), usando as ferramentas MCP já conectadas à conta
(Google Drive, e as que forem entrando conforme as próximas skills forem
desenhadas).

## Catálogo

| Skill | Dispara por fala? | Papel |
|---|---|---|
| `criar-cliente` | sim | garante a estrutura padrão de pastas do cliente no Drive |
| `criar-site` | sim | gera o site do cliente (React + Next.js, com 3D/vídeo condicional) a partir das referências do Drive, usando impeccable como espinha dorsal de direção/construção/QA |
| `post-instagram` | sim / cron | publica no Instagram (@aidealab7) o próximo conteúdo aprovado em `06-Aprovados-para-Postar`, via Graph API — não gera conteúdo, só publica o que já está aprovado |

Planejada, com spec própria em `docs/superpowers/specs/` antes de virar
skill (ainda não criada, ainda não mesclada neste branch): **criar
carrossel** (`criar-post`) — é ela quem alimenta `06-Aprovados-para-Postar`
que o `post-instagram` consome.
Todas dependem de `criar-cliente` para localizar a pasta certa do cliente.

## Convenções

- Uma pasta por skill, `SKILL.md` (+ `references/*.md` quando a skill precisar
  de código ou tabela de apoio).
- Skill descreve só instrução — sem script externo. As chamadas MCP citadas no
  `SKILL.md` são as ferramentas reais já conectadas à conta, não aliases (ao
  contrário do agente de processo, aqui não há necessidade de indireção porque
  não há reexportação para outro ambiente).
