#!/bin/bash
# Quick script to prepare for Render deployment

echo "🚀 Подготовка за Render Deployment"
echo "===================================="
echo ""

# Check if .env is in .gitignore
if git check-ignore .env > /dev/null 2>&1; then
    echo "✅ .env файлът е в .gitignore (безопасно)"
else
    echo "⚠️  .env файлът НЕ е в .gitignore!"
    echo "   Добави '.env' в .gitignore преди push!"
    exit 1
fi

# Check Dockerfile
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile съществува"
else
    echo "❌ Dockerfile липсва!"
    exit 1
fi

# Check requirements.txt
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt съществува"
else
    echo "❌ requirements.txt липсва!"
    exit 1
fi

# Check git status
echo ""
echo "📊 Git Status:"
git status --short | head -10

echo ""
echo "===================================="
echo ""
echo "📝 Следващи стъпки:"
echo ""
echo "1. Commit промените:"
echo "   git add ."
echo "   git commit -m 'Ready for Render deployment'"
echo ""
echo "2. Push в GitHub:"
echo "   git push origin newone"
echo ""
echo "3. Отиди на render.com и:"
echo "   - New + → Web Service"
echo "   - Connect GitHub repo"
echo "   - Render автоматично детектира Dockerfile!"
echo ""
echo "Виж RENDER_STEPS_NOW.md за пълни инструкции!"
echo ""

