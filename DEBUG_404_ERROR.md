# 🔍 Debugging 404 грешка за www.marbaras.com

## Текущо състояние:
✅ Variables са правилно настроени:
- `DJANGO_ALLOWED_HOSTS` = `www.marbaras.com,marbaras-production.up.railway.app`
- `CSRF_TRUSTED_ORIGINS` = `https://www.marbaras.com,https://marbaras-production.up.railway.app`

## Стъпки за debugging:

### Стъпка 1: Провери Railway Logs

1. Отиди на Railway → **Logs** tab
2. Провери за следните грешки:

**Ако виждаш "DisallowedHost":**
- Проблемът е с `DJANGO_ALLOWED_HOSTS`
- Но вече е правилно настроен, така че може да е кеш проблем
- Решение: Изчакай 2-3 минути след промяна на Variables

**Ако виждаш "404 error: / from www.marbaras.com":**
- Това означава че Django получава заявката правилно
- Проблемът може да е с URL routing
- Провери дали `ecommerce.urls` има правилни URL patterns

**Ако виждаш други грешки:**
- Сподели какво точно виждаш в logs

### Стъпка 2: Провери Railway Domains

1. Отиди на Railway → **Settings** → **Domains**
2. Провери статуса на `www.marbaras.com`:
   - 🟢 **Active** - домейнът е активен
   - 🟡 **Pending** - очаква DNS да се разпространи
   - 🔴 **Failed** - има проблем с DNS

**Ако е "Pending":**
- Изчакай още 15-30 минути
- Кликни "Check DNS" бутона

**Ако е "Failed":**
- Провери DNS в jump.bg
- Убеди се че CNAME за `www` е `rlvxys18.up.railway.app`

### Стъпка 3: Провери DNS разпространение

1. Отиди на: https://dnschecker.org/
2. Въведи: `www.marbaras.com`
3. Тип: `CNAME`
4. Провери дали всички сървъри показват `rlvxys18.up.railway.app`

**Ако някои сървъри показват стара стойност:**
- DNS все още не се е разпространил
- Изчакай още 30-60 минути

### Стъпка 4: Тествай Railway домейн

1. Отиди на `https://marbaras-production.up.railway.app`
2. Ако този домейн работи:
   - Проблемът е с custom domain (DNS или Railway конфигурация)
3. Ако и този не работи:
   - Проблемът е с приложението
   - Провери Railway logs за грешки

### Стъпка 5: Провери middleware

Има `WWWRedirectMiddleware` който редиректва `marbaras.com` към `www.marbaras.com`.

**Ако виждаш 404 на `marbaras.com` (без www):**
- Това е нормално - middleware трябва да редиректва към `www.marbaras.com`
- Ако не редиректва, провери middleware конфигурация

### Стъпка 6: Провери URL patterns

1. Провери `ecommerce/urls.py` за правилни URL patterns
2. Убеди се че има pattern за `/` (начална страница)

---

## Често срещани проблеми:

### Проблем 1: DNS все още не се е разпространил
**Симптоми:**
- Railway показва "Pending"
- DNS Checker показва различни стойности на различни сървъри

**Решение:**
- Изчакай още 30-60 минути
- DNS може да отнеме до 48 часа за пълно разпространение

### Проблем 2: Railway не е приел домейна
**Симптоми:**
- Railway показва "Failed" или "Incorrect DNS setup"

**Решение:**
- Провери DNS в jump.bg
- Убеди се че CNAME за `www` е точно `rlvxys18.up.railway.app`
- Кликни "Check DNS" в Railway

### Проблем 3: Django не приема домейна
**Симптоми:**
- Railway logs показват "DisallowedHost"
- Но Variables са правилни

**Решение:**
- Изчакай 2-3 минути след промяна на Variables
- Railway автоматично redeploy-ва след промяна на Variables
- Провери дали `DJANGO_DEBUG` е `False`

---

## Проверка:

След като направиш всички проверки, сподели:

1. Какво показва Railway → Settings → Domains за `www.marbaras.com`?
2. Какво виждаш в Railway logs (особено за "404" или "DisallowedHost")?
3. Работи ли `https://marbaras-production.up.railway.app`?
4. Какво показва DNS Checker за `www.marbaras.com`?

---

## Ако все още има проблеми:

1. Провери Railway logs за конкретни грешки
2. Убеди се че всички Variables са правилно настроени
3. Провери DNS разпространение с DNS Checker
4. Тествай Railway домейн (`marbaras-production.up.railway.app`)
5. Сподели:
   - Railway logs (последните 50-100 реда)
   - Статус на домейна в Railway
   - Резултати от DNS Checker

