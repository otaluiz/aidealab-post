#!/bin/bash
# Setup script para habilitar publicação cloud

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Setup - Instagram Cloud Publishing                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check requirements
if ! command -v git &> /dev/null; then
    echo "❌ git não encontrado. Instale git primeiro."
    exit 1
fi

echo "1️⃣  Verificando GitHub secrets..."
echo ""
echo "Você precisa adicionar os seguintes secrets no GitHub:"
echo "  • INSTAGRAM_ACCESS_TOKEN"
echo "  • INSTAGRAM_BUSINESS_ACCOUNT_ID"
echo "  • SUPABASE_SERVICE_ROLE_KEY"
echo "  • SUPABASE_URL"
echo ""
echo "Local: https://github.com/otaluiz/aidealab-post/settings/secrets/actions"
echo ""
read -p "Pressione ENTER quando tiver adicionado os secrets..."

echo ""
echo "2️⃣  Verificando Supabase..."
if command -v supabase &> /dev/null; then
    echo "✓ Supabase CLI encontrada"
    read -p "Deploy Edge Function agora? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        supabase functions deploy publish-instagram --no-verify-jwt
        echo "✓ Edge Function deployed"
    fi
else
    echo "⚠️  Supabase CLI não encontrada"
    echo "Install: npm install -g supabase"
fi

echo ""
echo "3️⃣  Configurando workflows..."
echo "Workflows automáticos habilitados:"
echo "  ✓ post-instagram-cloud.yml (a cada 30 min)"
echo "  ✓ post-instagram-daily.yml (diário)"

echo ""
echo "✅ Setup completo!"
echo ""
echo "Próximos passos:"
echo "  1. Verifique fila: agente\ aidealab/skills/post-instagram/queue/"
echo "  2. Primeira publicação: https://github.com/otaluiz/aidealab-post/actions/workflows/post-instagram-cloud.yml"
echo "  3. Docs: CLOUD_ARCHITECTURE.md"
echo ""
