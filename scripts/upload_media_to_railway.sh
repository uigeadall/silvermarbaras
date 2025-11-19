#!/bin/bash
# Скрипт за качване на media файловете в Railway Volume

set -e

echo "=========================================="
echo "Качване на Media Файловете в Railway"
echo "=========================================="

# Проверка дали Railway CLI е инсталиран
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI не е инсталиран!"
    echo "Инсталирай го с: npm i -g @railway/cli"
    exit 1
fi

# Проверка дали е свързан към проект
if ! railway status &> /dev/null; then
    echo "⚠️  Не си свързан към Railway проект"
    echo "Изпълни: railway link"
    exit 1
fi

# Проверка дали media директорията съществува
if [ ! -d "media/products" ]; then
    echo "❌ media/products директорията не съществува!"
    exit 1
fi

echo "✅ Railway CLI е инсталиран и свързан"
echo ""

# Покажи статистика
TOTAL_FILES=$(find media/products -type f | wc -l | tr -d ' ')
TOTAL_SIZE=$(du -sh media/products | cut -f1)

echo "📊 Статистика:"
echo "   - Общо файлове: $TOTAL_FILES"
echo "   - Общ размер: $TOTAL_SIZE"
echo ""

# Потвърждение
read -p "Продължи с качването? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Отказано."
    exit 0
fi

echo ""
echo "🚀 Започвам качването..."
echo ""

# Проверка дали Volume е монтиран
echo "🔍 Проверявам дали Volume е монтиран..."
echo ""

# Опитай да провериш дали директорията съществува
VOLUME_CHECK=$(railway run bash -c "ls -la /app 2>&1 | head -5" 2>&1)
echo "📋 Съдържание на /app:"
echo "$VOLUME_CHECK" | grep -v "^$" | head -5
echo ""

# Проверка дали /app/media съществува
MEDIA_CHECK=$(railway run bash -c "test -d /app/media && echo 'EXISTS' || echo 'NOT_FOUND'" 2>&1 | tail -1 | tr -d '[:space:]')

if [ "$MEDIA_CHECK" != "EXISTS" ]; then
    echo "⚠️  ВНИМАНИЕ: /app/media не е намерен!"
    echo ""
    echo "Възможни причини:"
    echo "1. Volume не е създаден в Railway Dashboard"
    echo "2. Volume е създаден, но не е направен redeploy"
    echo "3. Mount Path не е правилно настроен"
    echo ""
    echo "Проверка в Railway Dashboard:"
    echo "1. Отиди на Railway Dashboard → твоя проект → service 'marbaras'"
    echo "2. Settings → Volumes"
    echo "3. Провери дали 'marbaras-volume' съществува"
    echo "4. Провери дали Mount Path е точно '/app/media'"
    echo "5. Ако Volume съществува, направи REDEPLOY на service-а"
    echo ""
    
    # Питай дали да продължи все пак
    read -p "Продължи с опит за качване все пак? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Отказано. Направи redeploy и опитай отново."
        exit 1
    fi
    echo ""
    echo "⚠️  Продължавам с опит за качване, но може да не работи..."
    echo ""
else
    echo "✅ Volume е монтиран на /app/media"
    echo ""
fi

# Създай директориите в Railway Volume (ако не съществуват)
echo "📁 Създавам директории..."
railway run bash -c "mkdir -p /app/media/products /app/media/products/multiple" || {
    echo "⚠️  Грешка при създаване на директории (може би вече съществуват)"
}

# Качи файловете
echo "📤 Качвам файловете..."
echo "Това може да отнеме време в зависимост от размера..."

# Използвай tar за по-бързо качване
cd media
tar -czf /tmp/media_products.tar.gz products/ 2>/dev/null || {
    echo "⚠️  Грешка при създаване на архив"
    exit 1
}

# Качи архива и го разпакувай в Railway
echo "📦 Качвам архив (това може да отнеме време)..."
railway run bash -c "cd /app/media && tar -xzf -" < /tmp/media_products.tar.gz || {
    echo ""
    echo "⚠️  Грешка при качване на файловете"
    echo "Възможни причини:"
    echo "1. Volume не е правилно монтиран"
    echo "2. Няма достатъчно място в Volume"
    echo "3. Проблем с правата за достъп"
    echo ""
    echo "Опитай да качиш файловете чрез Admin Panel или провери Railway logs."
    rm -f /tmp/media_products.tar.gz
    exit 1
}

# Изтрий временния архив
rm -f /tmp/media_products.tar.gz
cd ..

echo ""
echo "✅ Готово! Media файловете са качени в Railway Volume."
echo ""
echo "Следващи стъпки:"
echo "1. Провери в Railway Dashboard дали файловете са там"
echo "2. Провери в приложението дали снимките се показват"
echo "3. Направи redeploy и провери дали файловете се запазват"

