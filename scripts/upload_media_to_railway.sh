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
VOLUME_CHECK=$(railway run bash -c "test -d /app/media && echo 'OK' || echo 'MISSING'" 2>&1 | tail -1)
if [ "$VOLUME_CHECK" != "OK" ]; then
    echo ""
    echo "❌ ГРЕШКА: Railway Volume не е монтиран!"
    echo ""
    echo "Трябва да създадеш Volume в Railway Dashboard:"
    echo "1. Отиди на Railway Dashboard → твоя проект → твоя service"
    echo "2. Settings → Volumes"
    echo "3. '+ New Volume'"
    echo "4. Name: marbaras-volume (или каквото искаш)"
    echo "5. Mount Path: /app/media (ТОЧНО това!)"
    echo "6. Create"
    echo ""
    echo "След това направи redeploy и опитай отново."
    exit 1
fi

echo "✅ Volume е монтиран на /app/media"
echo ""

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

