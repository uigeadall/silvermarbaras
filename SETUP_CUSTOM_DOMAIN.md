# 🌐 Настройка на Custom Domain в Railway

## Стъпка 1: Добави Domain в Railway

1. Отиди на [Railway Dashboard](https://railway.app/)
2. Избери твоя проект **"marbaras"**
3. Кликни на **"Settings"** tab
4. Скролни надолу до **"Domains"** секция
5. Кликни **"Custom Domain"** или **"+ New Domain"**
6. Въведи твоя домейн (напр. `marbaras.jump.bg` или `www.marbaras.jump.bg`)
7. Railway ще покаже DNS записи които трябва да добавиш

---

## Стъпка 2: Настрой DNS в jump.bg

### Вариант A: Ако използваш поддомейн (напр. `marbaras.jump.bg`):

1. Влез в твоя jump.bg акаунт
2. Отиди на DNS настройките за домейна
3. Добави следните DNS записи:

#### CNAME запис (препоръчително):
```
Type: CNAME
Name: marbaras (или каквото искаш)
Value: marbaras-production.up.railway.app
TTL: 3600 (или автоматично)
```

#### ИЛИ A запис (ако CNAME не работи):
Railway ще ти даде IP адрес който трябва да използваш. Добави:
```
Type: A
Name: marbaras (или каквото искаш)
Value: [IP адрес от Railway]
TTL: 3600
```

### Вариант B: Ако използваш главен домейн (напр. `jump.bg`):

1. Влез в твоя jump.bg акаунт
2. Отиди на DNS настройките
3. Добави:

#### CNAME запис:
```
Type: CNAME
Name: @ (или празно, за главен домейн)
Value: marbaras-production.up.railway.app
TTL: 3600
```

#### ИЛИ A запис:
```
Type: A
Name: @ (или празно)
Value: [IP адрес от Railway]
TTL: 3600
```

---

## Стъпка 3: Проверка в Railway

1. След като добавиш DNS записите, Railway автоматично ще провери дали са правилни
2. Може да отнеме няколко минути до няколко часа за DNS да се разпространи
3. В Railway Dashboard → Settings → Domains ще видиш статуса:
   - 🟡 **Pending** - очаква DNS да се разпространи
   - 🟢 **Active** - домейнът е активен и работи
   - 🔴 **Failed** - има проблем с DNS записите

---

## Стъпка 4: Обнови Django Settings (ако е необходимо)

Railway автоматично настройва SSL сертификат, но трябва да се увериш че Django знае за новия домейн:

1. Отиди на Railway Dashboard → твоя проект → **Variables**
2. Провери/добави `DJANGO_ALLOWED_HOSTS`:
   ```
   DJANGO_ALLOWED_HOSTS=marbaras.jump.bg,www.marbaras.jump.bg
   ```
   (или какъвто е твоят домейн)

3. Провери/добави `CSRF_TRUSTED_ORIGINS`:
   ```
   CSRF_TRUSTED_ORIGINS=https://marbaras.jump.bg,https://www.marbaras.jump.bg
   ```

---

## Стъпка 5: Проверка

1. Изчакай 5-15 минути за DNS да се разпространи
2. Отиди на твоя домейн в браузър (напр. `https://marbaras.jump.bg`)
3. Трябва да видиш сайта
4. Провери дали SSL сертификатът работи (🔒 икона в браузъра)

---

## Често срещани проблеми:

### DNS не се разпространява:
- Изчакай до 24 часа (обикновено е по-бързо)
- Използвай [DNS Checker](https://dnschecker.org/) за да провериш дали DNS е разпространен навсякъде

### SSL сертификат не работи:
- Railway автоматично инсталира SSL сертификат
- Може да отнеме до 1 час след като DNS е активен
- Провери в Railway Dashboard → Settings → Domains дали SSL е "Active"

### 502 Bad Gateway:
- Провери дали приложението работи в Railway
- Провери Railway logs за грешки
- Убеди се че `DJANGO_ALLOWED_HOSTS` включва новия домейн

### CSRF грешки:
- Убеди се че `CSRF_TRUSTED_ORIGINS` включва новия домейн с `https://`
- Провери дали използваш правилния протокол (https, не http)

---

## Полезни команди за проверка:

### Проверка на DNS:
```bash
# Проверка на CNAME
dig marbaras.jump.bg CNAME

# Проверка на A запис
dig marbaras.jump.bg A

# Проверка на всички записи
nslookup marbaras.jump.bg
```

### Проверка на SSL:
```bash
# Проверка на SSL сертификат
openssl s_client -connect marbaras.jump.bg:443 -servername marbaras.jump.bg
```

---

## След като домейнът работи:

1. Обнови Stripe Webhook URL:
   - Отиди на Stripe Dashboard → Developers → Webhooks
   - Обнови endpoint URL на: `https://marbaras.jump.bg/webhook/`
   - Обнови `STRIPE_WEBHOOK_SECRET` в Railway Variables

2. Обнови всички линкове в сайта (ако има hardcoded URLs)

3. Тествай всички функционалности с новия домейн

---

**Готово!** 🎉 След като DNS се разпространи, домейнът трябва да работи.

