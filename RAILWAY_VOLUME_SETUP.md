# 🚨 КРИТИЧНО: Настройка на Railway Volume за Media Файловете

## Проблем
В Railway файловата система е **ефемерна** - всички файлове се изтриват при всеки redeploy. Това означава:
- ❌ Снимките на продуктите се изтриват
- ❌ Банерът не се показва
- ❌ Всички качени файлове се губят

## Решение: Railway Volume (ЗАДЪЛЖИТЕЛНО)

### Стъпка 1: Създай Volume в Railway Dashboard

1. **Отиди на Railway Dashboard**: https://railway.app/dashboard
2. **Избери проекта си**
3. **Избери service-а** (обикновено `marbaras` или името на приложението)
4. **Отиди на таба "Settings"**
5. **Скролни до секцията "Volumes"**
6. **Кликни "+ New Volume"**
7. **Попълни:**
   - **Name**: `media-volume`
   - **Mount Path**: `/app/media` (ТОЧНО това!)
8. **Кликни "Create"**

⚠️ **ВАЖНО**: Volume трябва да бъде създаден ПРЕДИ да качваш нови продукти!

### Стъпка 2: Проверка след създаване на Volume

След като създадеш Volume:

1. **Redeploy service-а** (Railway автоматично ще го направи или кликни "Redeploy")
2. **Провери в logs** дали Volume е монтиран правилно
3. **Отиди на admin panel** и качи нова снимка
4. **Провери дали файлът се запазва** след redeploy

### Стъпка 3: Качи Старите Media Файлове

Ако вече имаш продукти с снимки, трябва да ги качиш отново:

#### Опция A: Качи чрез Admin Panel (Най-лесно)

1. Отиди на Django Admin: `https://твоя-домейн/admin/`
2. Отиди на **Products** → избери продукт
3. Качи снимките отново
4. Те ще се запазят в Volume

#### Опция B: Използвай Railway CLI

```bash
# Инсталирай Railway CLI
npm i -g @railway/cli

# Свържи се към проекта
railway link

# Намери service name-а
railway status

# Качи media файловете от локалната машина
railway run --service <service-name> bash -c "mkdir -p /app/media/products && mkdir -p /app/media/products/multiple"
# След това качи файловете чрез друг метод (scp, rsync, etc.)
```

### Стъпка 4: За Банерът (Static Файл)

Банерът е static файл и трябва да се качи в git или да се използва cloud storage.

#### Опция A: Качи в Git (Ако файлът не е твърде голям)

```bash
# Провери дали банерът е в git
git ls-files | grep banner

# Ако не е, добави го
git add static/images/banner.jpg
git commit -m "Add banner image"
git push github newone
```

#### Опция B: Използвай Cloud Storage (Препоръчително)

За по-добра производителност, използвай Cloudinary или AWS S3 за static файловете.

## Проверка

### Проверка 1: Дали Volume е монтиран

1. Отиди на Railway Dashboard → твоя service → **Deployments**
2. Кликни на последния deployment
3. Провери **logs** за съобщения като:
   - `Volume mounted at /app/media`
   - Или грешки свързани с Volume

### Проверка 2: Дали Media Файловете Работят

1. Отиди на приложението
2. Качи нова снимка чрез admin panel
3. Провери дали се показва
4. Направи redeploy
5. Провери дали снимката все още се показва (трябва да се запази!)

### Проверка 3: Дали Static Файловете Работят

1. Отвори Developer Tools (F12) → Network tab
2. Презареди страницата
3. Провери дали `/static/images/banner.jpg` се зарежда
4. Ако не се зарежда, провери Railway logs за `collectstatic`

## Често Срещани Проблеми

### Проблем 1: Volume не се монтира

**Решение:**
- Провери дали Mount Path е точно `/app/media` (не `/media` или друго)
- Провери дали Volume е създаден правилно
- Redeploy service-а

### Проблем 2: Файловете все още се изтриват

**Решение:**
- Увери се че Volume е създаден ПРЕДИ да качваш файлове
- Провери дали `MEDIA_ROOT` в settings.py е `/app/media`
- Провери Railway logs за грешки

### Проблем 3: Банерът не се показва

**Решение:**
- Провери дали `collectstatic` се изпълнява правилно
- Провери дали файлът е в git
- Провери дали static files се обслужват правилно

## Следващи Стъпки

1. ✅ **Създай Railway Volume** (`/app/media`)
2. ✅ **Redeploy service-а**
3. ✅ **Качи нови продукти** и провери дали снимките се запазват
4. ✅ **Качи банер** в git или cloud storage
5. ✅ **Тествай** дали всичко работи след redeploy

## Алтернатива: Cloud Storage (Препоръчително за Production)

За по-добра производителност и надеждност, препоръчвам да използваш cloud storage:

- **Cloudinary** (безплатно до 25GB) - https://cloudinary.com
- **AWS S3** (pay-as-you-go)
- **Railway Volume** (текущо решение - работи, но по-скъпо)

