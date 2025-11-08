# 🔧 Настройка на Stripe и Email - Стъпка по Стъпка

## 📧 Част 1: Настройка на Email

### Вариант A: Gmail (Най-лесно за започване)

#### Стъпка 1: Създай App Password в Google

1. Отиди на [Google Account](https://myaccount.google.com/)
2. Security → 2-Step Verification (трябва да е включено)
3. App passwords → Select app: "Mail" → Select device: "Other" → "Django"
4. Копирай генерирания 16-цифрен парола

#### Стъпка 2: Добави в .env файла

Отвори `.env` файла и добави/промени:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=sales@marbaras.com
ADMIN_EMAIL=admin@marbaras.com
```

**Важно:** 
- Използвай App Password, НЕ обикновената парола!
- Премахни интервалите от App Password (или ги остави, Django ги обработва)

#### Стъпка 3: Тествай

```bash
python3 manage.py test_emails --email your-email@gmail.com --type welcome
```

---

### Вариант B: SendGrid (Препоръчано за production)

#### Стъпка 1: Регистрация

1. Отиди на [SendGrid](https://sendgrid.com/)
2. Регистрирай се (безплатен план до 100 имейла/ден)
3. Verify your email

#### Стъпка 2: Създай API Key

1. Settings → API Keys → Create API Key
2. Name: "Django Production"
3. Permissions: "Full Access" (или само Mail Send)
4. Копирай API ключа (показва се само веднъж!)

#### Стъпка 3: Добави в .env

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.твоят-api-ключ-тук
DEFAULT_FROM_EMAIL=sales@marbaras.com
ADMIN_EMAIL=admin@marbaras.com
```

#### Стъпка 4: Verify Sender (Важно!)

1. SendGrid → Settings → Sender Authentication
2. Verify Single Sender или Domain
3. Следвай инструкциите

#### Стъпка 5: Тествай

```bash
python3 manage.py test_emails --email your-email@example.com
```

---

### Вариант C: Mailgun (Алтернатива)

#### Стъпка 1: Регистрация

1. Отиди на [Mailgun](https://www.mailgun.com/)
2. Регистрирай се (безплатен план до 5000 имейла/месец)

#### Стъпка 2: Добави в .env

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=твоят-mailgun-password
DEFAULT_FROM_EMAIL=sales@marbaras.com
```

---

## 💳 Част 2: Настройка на Stripe

### Стъпка 1: Влез в Stripe Dashboard

1. Отиди на [Stripe Dashboard](https://dashboard.stripe.com/)
2. Влез в акаунта си (или създай нов)

### Стъпка 2: Development (Test Mode) - За тестване

#### Получи Test Keys:

1. Dashboard → Developers → API keys
2. Убеди се че си в **Test mode** (toggle в горния десен ъгъл)
3. Копирай:
   - **Publishable key** (зад започва с `pk_test_`)
   - **Secret key** (зад започва с `sk_test_`)

#### Добави в .env:

```env
STRIPE_SECRET_KEY=sk_test_твоят-test-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_твоят-test-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_твоят-webhook-secret
```

### Стъпка 3: Production (Live Mode) - За реален сайт

#### ВАЖНО: Използвай Live keys само в production!

1. Dashboard → Toggle на **Live mode** (в горния десен ъгъл)
2. Developers → API keys
3. Копирай:
   - **Publishable key** (зад започва с `pk_live_`)
   - **Secret key** (зад започва с `sk_live_`)

#### Добави в .env (PRODUCTION):

```env
STRIPE_SECRET_KEY=sk_live_твоят-live-secret-key
STRIPE_PUBLISHABLE_KEY=pk_live_твоят-live-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_твоят-live-webhook-secret
```

### Стъпка 4: Настрой Webhook Endpoint

#### За Development (Test Mode):

1. Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `http://localhost:8000/webhook/` (за local тестване)
   или `https://yourdomain.com/webhook/` (за production)
4. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
5. Click "Add endpoint"
6. Копирай **Signing secret** (зад започва с `whsec_`)
7. Добави в `.env` като `STRIPE_WEBHOOK_SECRET`

#### За Production (Live Mode):

1. Убеди се че си в **Live mode**
2. Същите стъпки, но използвай production URL
3. Endpoint URL: `https://yourdomain.com/webhook/`

### Стъпка 5: Тествай Stripe

#### Тествай с Test Card:

1. Отиди на checkout страницата
2. Използвай тестова карта:
   - **Card number:** `4242 4242 4242 4242`
   - **Expiry:** Всяка бъдеща дата (напр. `12/25`)
   - **CVC:** Всяка 3 цифри (напр. `123`)
   - **ZIP:** Всяка 5 цифри (напр. `12345`)

3. Провери в Stripe Dashboard → Payments дали се появява

#### Други Test Cards:

- **Decline:** `4000 0000 0000 0002`
- **3D Secure:** `4000 0025 0000 3155`
- **Requires Auth:** `4000 0027 6000 3184`

### Стъпка 6: Проверка на Webhook

1. Stripe Dashboard → Developers → Webhooks
2. Кликни на твоя endpoint
3. Провери "Recent deliveries" - трябва да видиш успешни заявки

---

## ✅ Проверка на Настройките

### Проверка на Email:

```bash
# Тествай welcome email
python3 manage.py test_emails --email your-email@example.com --type welcome

# Тествай order confirmation
python3 manage.py test_emails --email your-email@example.com --type order
```

### Проверка на Stripe:

```python
# В Django shell
python3 manage.py shell
>>> from django.conf import settings
>>> print("Stripe Secret:", settings.STRIPE_SECRET_KEY[:10] + "...")
>>> print("Stripe Publishable:", settings.STRIPE_PUBLISHABLE_KEY[:10] + "...")
```

### Проверка на Webhook:

1. Направи тестова поръчка
2. Провери в Stripe Dashboard → Webhooks → Recent deliveries
3. Трябва да видиш успешна заявка

---

## 🔒 Security Best Practices

### Email:
- ✅ Никога не комитирай пароли в git
- ✅ Използвай App Passwords за Gmail
- ✅ Използвай production SMTP за production
- ✅ Verify sender domain (SPF/DKIM)

### Stripe:
- ✅ Използвай Test keys за development
- ✅ Използвай Live keys само в production
- ✅ Никога не комитирай keys в git
- ✅ Валидирай webhook signatures
- ✅ Използвай HTTPS за webhooks

---

## 🆘 Troubleshooting

### Email не се изпраща:

1. **Gmail:**
   - Провери дали 2-Step Verification е включено
   - Провери дали използваш App Password (не обикновена парола)
   - Провери spam папката

2. **SendGrid:**
   - Провери дали sender е verified
   - Провери API key permissions
   - Провери Activity feed в SendGrid

3. **Общи:**
   - Провери логове: `tail -f logs/django.log`
   - Тествай с console backend: `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`

### Stripe не работи:

1. Провери дали keys са правилни (test vs live)
2. Провери дали webhook URL е правилен
3. Провери Stripe Dashboard за errors
4. Провери логове: `tail -f logs/django.log`

### Webhook не работи:

1. Провери дали `STRIPE_WEBHOOK_SECRET` е правилен
2. Провери дали endpoint е достъпен (не localhost за production)
3. Провери Stripe Dashboard → Webhooks → Recent deliveries
4. Провери дали има SSL сертификат (HTTPS)

---

## 📝 Примерен .env файл

```env
# Email (Gmail пример)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=sales@marbaras.com
ADMIN_EMAIL=admin@marbaras.com

# Stripe (Test Mode пример)
STRIPE_SECRET_KEY=sk_test_51AbCdEf...
STRIPE_PUBLISHABLE_KEY=pk_test_51AbCdEf...
STRIPE_WEBHOOK_SECRET=whsec_AbCdEf123...
```

---

## ✅ Checklist

### Email:
- [ ] Избран email provider (Gmail/SendGrid/Mailgun)
- [ ] Настроени credentials в `.env`
- [ ] Тестван email изпращане
- [ ] Sender verified (за SendGrid/Mailgun)
- [ ] SPF/DKIM записи (опционално, но препоръчано)

### Stripe:
- [ ] Test keys добавени в `.env`
- [ ] Webhook endpoint създаден
- [ ] Webhook secret добавен в `.env`
- [ ] Тествана поръчка с test card
- [ ] Проверен webhook в Stripe Dashboard
- [ ] Live keys готови за production (когато е време)

---

**Следваща стъпка:** Настрой `.env` файла и тествай! 🚀

