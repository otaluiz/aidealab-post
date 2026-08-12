---
name: criar-cliente
description: Garante que a pasta de um cliente da aidealab existe no Google Drive com a estrutura padrão de subpastas, criando o que faltar sem duplicar o que já existe. Dispara com "crie cliente <nome>" / "novo cliente <nome>". Idempotente — também serve para completar a estrutura de um cliente já existente.
---

# Criar cliente

Garante, no Google Drive, que a pasta de um cliente dentro de `Clientes`
(parentId `1xHuFxkYD0INTpdZbzBZLRBy-X3tVM-rv`) existe e contém a estrutura
padrão de subpastas — criando apenas o que faltar. É a base das demais skills
da agência (criar carrossel, postar no Instagram, criar site): elas localizam
a pasta do cliente certo a partir da estrutura que esta skill garante.

## Quando usar

Pedido do tipo "crie cliente X" ou "novo cliente X". Também serve para
completar a estrutura de um cliente que já existe mas está incompleto (ex:
cliente com só uma pasta de logo solta) — não é exclusivo de cliente novo.

## Estrutura padrão

```
00-Identidade-e-Tom
01-Referencias/
  Instagram
  Site
  Video
02-Materiais-Brutos
03-Roteiros
04-Carrosseis
05-Campanhas
06-Aprovados-para-Postar
```

Lista hardcoded aqui — não é lida dinamicamente de nenhuma pasta modelo a cada
execução. Se o padrão mudar, editar esta lista.

## Ferramentas necessárias

MCP do Google Drive já conectado à conta. Usa apenas:
- `search_files` — checar existência por `parentId` + `title`.
- `create_file` com `mimeType: application/vnd.google-apps.folder` — criar
  pasta (cliente, pasta de topo, subpasta de `01-Referencias`).

Não há ferramenta de renomear/mover/deletar no Drive MCP conectado. Qualquer
correção desse tipo fica a cargo do usuário, manualmente.

## Procedimento

1. **Receber o nome do cliente** do pedido do usuário.
2. **Normalizar para minúsculas** — padrão observado nas pastas existentes
   ("hora da chipa", "cantinho mineiro", "sieger"). Evita duplicar cliente por
   diferença de maiúscula/minúscula.
3. **Buscar dentro de `Clientes`** (parentId fixo acima) por pasta cujo título
   bata, case-insensitive, com o nome normalizado.
4. **Se não existir, criar a pasta do cliente** dentro de `Clientes`.
5. **Garantir as 7 pastas de topo** do template dentro da pasta do cliente,
   criando só as que faltarem.
6. **Garantir as 3 subpastas de `01-Referencias`** (`Instagram`, `Site`,
   `Video`) — criando `01-Referencias` primeiro se ela também faltar.
7. **Reportar**: link da pasta do cliente no Drive, e quais pastas foram
   criadas agora vs. já existiam antes.

A skill é idempotente: rodar de novo sobre um cliente já completo não duplica
nada, só confirma que a estrutura está presente.

## O que reportar sempre

- Link da pasta do cliente no Drive.
- Lista do que foi criado nesta execução vs. do que já existia.
- Se encontrar uma pasta de nome parecido mas não idêntico (ex: variação de
  grafia), avisar antes de criar uma pasta nova — pode ser o mesmo cliente.

## Fora de escopo

- Copiar arquivos/templates para dentro das subpastas — só a estrutura de
  pastas é replicada, não conteúdo (todas as subpastas do modelo estão vazias).
- Renomear, mover ou deletar pastas de clientes existentes — inclusive a pasta
  antiga `01-Referencias-Instagram`, que deve ser removida manualmente pelo
  usuário quando encontrada.
- As demais skills da agência (criar carrossel, postar no Instagram, criar
  site) — cada uma com sua própria spec e skill, ainda não criadas.
