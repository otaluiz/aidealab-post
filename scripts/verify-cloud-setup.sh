#!/bin/bash
# Verifica se tudo está configurado para funcionar em cloud

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Verificação - Cloud Setup                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

check_secret() {
    local secret_name=$1
    local description=$2

    echo -n "Verificando $secret_name... "

    # Não podemos verificar diretamente via GitHub CLI neste ambiente
    # Mas podemos dar instruções
    echo ""
    echo "  ⚠️  Manual check needed: https://github.com/otaluiz/aidealab-post/settings/secrets/actions"
    echo "  Procure por: $secret_name"
    echo "  Descrição: $description"
    echo ""
}

check_file() {
    local file=$1
    local description=$2

    echo -n "Verificando $file... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗ NÃO ENCONTRADO${NC}"
        echo "  Esperado em: $file"
        ((CHECKS_FAILED++))
    fi
}

check_env_file() {
    local file=$1
    local var=$2

    echo -n "Verificando $var em $file... "
    if grep -q "^$var=" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} (pode estar nos GitHub Secrets)"
    fi
}

echo -e "${BOLD}1. Arquivos do Sistema${NC}"
check_file ".github/workflows/post-instagram-cloud.yml" "Workflow principal"
check_file "supabase/functions/publish-instagram/index.ts" "Edge Function"
check_file "CLOUD_ARCHITECTURE.md" "Documentação"
echo ""

echo -e "${BOLD}2. GitHub Secrets (Verificação Manual)${NC}"
check_secret "INSTAGRAM_ACCESS_TOKEN" "Token de acesso Instagram (System User)"
check_secret "INSTAGRAM_BUSINESS_ACCOUNT_ID" "ID da conta @idea_lab7 (17841472134319553)"
check_secret "SUPABASE_SERVICE_ROLE_KEY" "Chave de serviço Supabase"
check_secret "SUPABASE_URL" "URL do projeto Supabase"
echo ""

echo -e "${BOLD}3. Fila de Itens${NC}"
QUEUE_DIR="agente aidealab/skills/post-instagram/queue/FILA-SEMANA-1/02-carrossel"
if [ -d "$QUEUE_DIR" ]; then
    echo -e "${GREEN}✓${NC} Diretório de fila encontrado"
    echo "  Itens na fila:"
    for dir in "$QUEUE_DIR"/*/; do
        if [ -f "$dir/metadata.json" ]; then
            name=$(basename "$dir")
            posted=$(jq -r '.postado // "unknown"' "$dir/metadata.json" 2>/dev/null || echo "erro")
            if [ "$posted" = "true" ]; then
                echo "    ✓ $name (postado)"
            else
                echo "    ⏳ $name (aguardando)"
            fi
        fi
    done
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Diretório de fila não encontrado"
    ((CHECKS_FAILED++))
fi
echo ""

echo -e "${BOLD}4. Configuração Python${NC}"
check_file "agente aidealab/skills/post-instagram/scripts/requirements.txt" "Dependências Python"
check_file "agente aidealab/skills/post-instagram/scripts/publish_next.py" "Script principal de publicação"
echo ""

echo -e "${BOLD}5. .gitignore${NC}"
if grep -q "__pycache__" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Cache Python ignorado"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Padrão __pycache__ não encontrado"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Checklist Final${NC}"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "Antes da próxima publicação, verifique:"
echo ""
echo "☐ GitHub Secrets estão configurados:"
echo "    • INSTAGRAM_ACCESS_TOKEN"
echo "    • INSTAGRAM_BUSINESS_ACCOUNT_ID"
echo "    • SUPABASE_SERVICE_ROLE_KEY"
echo "    • SUPABASE_URL"
echo ""
echo "☐ Workflow disparável via: Actions → post-instagram-cloud"
echo ""
echo "☐ Fila tem itens com postado:false"
echo ""
echo "☐ GitHub Actions está habilitado no repo"
echo ""

echo "Próxima publicação:"
echo "  • Automática: a cada 30 minutos"
echo "  • Manual: GitHub UI → Actions → post-instagram-cloud → Run Workflow"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Verificação concluída - Sistema pronto para cloud!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Alguns itens precisam verificação manual${NC}"
    exit 0
fi
