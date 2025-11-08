# ✅ Проверка на Текущите Настройки

## 📊 Текущо Състояние

### Stripe ✅
- **Secret Key:** Настроен (test mode)
- **Publishable Key:** Настроен (test mode)
- **Webhook Secret:** Трябва да се провери

### Email ⚠️
- **Host:** Mailtrap Sandbox (за тестване)
- **User:** Настроен
- **Status:** Работи, но не изпраща реални имейли

---

## 🔧 Какво Трябва да Направиш

### 1. Проверка на Stripe Webhook Secret

Провери дали имаш `STRIPE_WEBHOOK_SECRET` в `.env`:

```bash
# Провери в .env файла
grep STRIPE_WEBHOOK_SECRET .env
```

Ако липсва:

1. Отиди в [Stripe Dashboard](https://dashboard.stripe.com/test/webhooks)
2. Кликни на твоя webhook endpoint (или създай нов)
3. Копирай "Signing secret" (започва с `whsec_`)
4. Добави в `.env`:
```env
STRIPE_WEBHOOK_SECRET=whsec_твоят-secret-тук
```

### 2. Настройка на Реален Email

Текущо използваш Mailtrap Sandbox. За production трябва реален SMTP.

**Избери един от вариантите:**

#### A. Gmail (5 минути)
1. Google Account → Security → 2-Step Verification → App Passwords
2. Генерирай App Password
3. В `.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=твоят-app-password
```

#### B. SendGrid (10 минути, препоръчано)
1. Регистрирай се на sendgrid.com
2. Settings → API Keys → Create API Key
3. В `.env`:
```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.твоят-api-key
```

### 3. Тестване

#### Тествай Email:
```bash
python3 manage.py test_emails --email your-real-email@example.com --type welcome
```

#### Тествай Stripe:
1. Отиди на checkout
2. Използвай тестова карта: `4242 4242 4242 4242`
3. Провери в Stripe Dashboard → Payments

---

## 📝 Бърз Checklist

### Stripe:
- [x] Secret Key настроен
- [x] Publishable Key настроен
- [ ] Webhook Secret проверен/добавен
- [ ] Webhook endpoint създаден в Stripe Dashboard
- [ ] Тествана поръчка с test card

### Email:
- [x] Email backend работи (Mailtrap)
- [ ] Production SMTP избран (Gmail/SendGrid/Mailgun)
- [ ] Production credentials добавени в `.env`
- [ ] Тестван email изпращане
- [ ] Sender verified (за SendGrid/Mailgun)

---

## 🚀 Следващи Стъпки

1. **Сега:** Провери/добави `STRIPE_WEBHOOK_SECRET` в `.env`
2. **Сега:** Настрой реален email (Gmail е най-бързо)
3. **След това:** Тествай всичко
4. **За production:** Смени на Live Stripe keys

---

Виж `SETUP_STRIPE_EMAIL.md` за пълни инструкции! 📚

