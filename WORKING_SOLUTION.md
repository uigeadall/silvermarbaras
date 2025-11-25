# ✅ Решение: Как да заработи www.marbaras.com

## Текущо състояние:
- ✅ CNAME за `www` → `rlvxys18.up.railway.app` (правилно в jump.bg)
- ❌ Railway очаква CNAME за `@` (root domain), но jump.bg не позволява това
- ⚠️ Railway показва "Incorrect DNS setup" за root domain

## Решение: Използвай само www поддомейн

### Стъпка 1: Изчакай DNS разпространение (30-60 минути)

DNS промените трябва да се разпространят глобално. Изчакай 30-60 минути.

### Стъпка 2: Провери DNS разпространение

1. Отиди на: https://dnschecker.org/
2. Въведи: `www.marbaras.com`
3. Тип: `CNAME`
4. Провери дали повечето сървъри показват `rlvxys18.up.railway.app`

**Ако повечето сървъри показват `rlvxys18.up.railway.app`:**
- DNS е разпространен ✅
- Продължи към Стъпка 3

**Ако повечето сървъри все още показват `marbaras.com`:**
- DNS все още не се е разпространил
- Изчакай още 30-60 минути

### Стъпка 3: Тествай www.marbaras.com

1. Отиди на `https://www.marbaras.com` в браузъра
2. Ако работи:
   - ✅ Готово! Сайтът работи
   - Railway може да показва грешка за root domain, но това не пречи на `www`

3. Ако не работи:
   - Провери Railway logs за грешки
   - Провери дали Variables са правилно настроени

### Стъпка 4: Ако все още не работи - провери Variables

1. Отиди на Railway → Settings → Variables
2. Убеди се че имаш:
   - `DJANGO_ALLOWED_HOSTS` = `www.marbaras.com,marbaras-production.up.railway.app`
   - `CSRF_TRUSTED_ORIGINS` = `https://www.marbaras.com,https://marbaras-production.up.railway.app`
   - `DJANGO_DEBUG` = `False`

---

## Алтернативно решение: Използвай Cloudflare за DNS

Ако искаш root domain (`marbaras.com`) също да работи:

### Стъпка 1: Създай Cloudflare акаунт

1. Отиди на: https://cloudflare.com
2. Създай безплатен акаунт
3. Добави домейна `marbaras.com`

### Стъпка 2: Промени nameservers-ите

1. Cloudflare ще ти даде nameservers (напр. `ns1.cloudflare.com`)
2. Отиди на регистратора на домейна (където си регистрирал `marbaras.com`)
3. Промени nameservers-ите да сочат към Cloudflare nameservers

### Стъпка 3: Конфигурирай DNS в Cloudflare

1. Отиди на Cloudflare Dashboard → DNS
2. Добави CNAME запис:
   - Име: `@` (root domain)
   - Стойност: `rlvxys18.up.railway.app`
   - Proxy: Изключено (само DNS)
3. Добави CNAME запис:
   - Име: `www`
   - Стойност: `rlvxys18.up.railway.app`
   - Proxy: Изключено (само DNS)

### Стъпка 4: Изчакай DNS разпространение

1. Изчакай 15-30 минути
2. Провери в Railway → Settings → Domains
3. Railway трябва да покаже "Active" за `www.marbaras.com`

---

## Препоръчително решение: Използвай само www

Най-лесното решение е да използваш само `www.marbaras.com`:

1. ✅ CNAME за `www` е вече правилно конфигуриран
2. ✅ Изчакай DNS да се разпространи (30-60 минути)
3. ✅ Тествай `https://www.marbaras.com`
4. ✅ Railway може да показва грешка за root domain, но `www` ще работи

---

## Проверка:

След 30-60 минути:

1. DNS Checker - трябва да показва `rlvxys18.up.railway.app` за `www.marbaras.com`
2. Браузър - `https://www.marbaras.com` трябва да работи
3. Railway - може да показва грешка за root domain, но това не пречи на `www`

---

## Ако след 2 часа все още не работи:

1. Провери Railway logs за конкретни грешки
2. Провери дали Variables са правилно настроени
3. Провери DNS разпространение с DNS Checker
4. Сподели:
   - Какво показват Railway logs
   - Какво показва DNS Checker
   - Какви грешки виждаш в браузъра

