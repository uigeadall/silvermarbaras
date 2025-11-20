# 🔗 Настройка на Stripe - Стъпка по Стъпка

## ✅ Текущо състояние

Stripe вече е интегриран в проекта! Трябва само да добавиш API ключовете.

---

## 📋 Стъпка 1: Вземи Stripe API Keys

### За Development/Test (използвай това първо):

1. Отиди на [Stripe Dashboard](https://dashboard.stripe.com/)
2. Влез в акаунта си (или създай нов безплатен акаунт)
3. Убеди се че си в **Test mode** (toggle в горния десен ъгъл)
4. Отиди на **Developers** → **API keys**
5. Копирай:
   - **Publishable key** (започва с `pk_test_...`)
   - **Secret key** (кликни "Reveal test key" - започва с `sk_test_...`)

### За Production (след като тестваш):

1. Toggle на **Live mode** в Stripe Dashboard
2. Отиди на **Developers** → **API keys**
3. Копирай Live keys (започват с `pk_live_...` и `sk_live_...`)

---

## 🚀 Стъпка 2: Добави Keys в Railway

### Ако използваш Railway:

1. Отиди на [Railway Dashboard](https://railway.app/)
2. Избери твоя проект/service
3. Кликни на **"Variables"** tab
4. Добави следните environment variables:

```env
STRIPE_SECRET_KEY=sk_test_твоят-test-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_твоят-test-publishable-key
```

**ВАЖНО:** За production използвай `sk_live_...` и `pk_live_...` вместо `sk_test_...` и `pk_test_...`

5. Railway автоматично ще redeploy-не приложението

---

## 🔔 Стъпка 3: Настрой Webhook (Опционално, но препоръчано)

Webhook-ът позволява на Stripe да уведомява приложението за успешни плащания.

### За Development (Test Mode):

1. В Stripe Dashboard → **Developers** → **Webhooks**
2. Кликни **"Add endpoint"**
3. Endpoint URL: `https://твоят-railway-url.railway.app/webhook/`
   - Намери URL-а в Railway Dashboard → Service → **"Settings"** → **"Domains"**
4. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
5. Кликни **"Add endpoint"**
6. Копирай **Signing secret** (започва с `whsec_...`)
7. Добави в Railway Variables:
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_твоят-webhook-secret
   ```

### За Production (Live Mode):

1. Убеди се че си в **Live mode**
2. Същите стъпки, но използвай production URL
3. Endpoint URL: `https://твоят-domain.com/webhook/`

---

## 🧪 Стъпка 4: Тествай Stripe

### Тествай с Test Card:

1. Отиди на checkout страницата на сайта
2. Използвай тестова карта:
   - **Card number:** `4242 4242 4242 4242`
   - **Expiry:** Всяка бъдеща дата (напр. `12/25`)
   - **CVC:** Всяка 3 цифри (напр. `123`)
   - **ZIP:** Всяка 5 цифри (напр. `12345`)

3. Провери в Stripe Dashboard → **Payments** дали се появява плащането

### Други Test Cards:

- **Decline:** `4000 0000 0000 0002`
- **3D Secure:** `4000 0025 0000 3155`
- **Requires Auth:** `4000 0027 6000 3184`

---

## ✅ Проверка

### Провери дали Stripe работи:

1. Отиди на health endpoint: `https://твоят-url.railway.app/health/`
2. Трябва да видиш:
   ```json
   {
     "status": "healthy",
     "checks": {
       "stripe": "configured"
     }
   }
   ```

### Провери Webhook:

1. Stripe Dashboard → **Developers** → **Webhooks**
2. Кликни на твоя endpoint
3. Провери **"Recent deliveries"** - трябва да видиш успешни заявки след плащане

---

## 🔧 Ако имаш проблеми

### Stripe не работи:

1. Провери дали ключовете са правилно добавени в Railway Variables
2. Провери дали използваш правилния mode (Test vs Live)
3. Провери Railway logs за грешки
4. Убеди се че `STRIPE_SECRET_KEY` и `STRIPE_PUBLISHABLE_KEY` са добавени

### Webhook не работи:

1. Провери дали `STRIPE_WEBHOOK_SECRET` е добавен
2. Провери дали webhook URL е правилен в Stripe Dashboard
3. Провери Railway logs за webhook грешки

---

## 📚 Полезни линкове

- [Stripe Dashboard](https://dashboard.stripe.com/)
- [Stripe API Keys](https://dashboard.stripe.com/apikeys)
- [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
- [Stripe Test Cards](https://stripe.com/docs/testing)

---

## 💡 Следващи стъпки

След като тестваш с Test keys и всичко работи:

1. Смени на **Live mode** в Stripe Dashboard
2. Вземи Live API keys
3. Обнови Railway Variables с Live keys
4. Настрой Live webhook endpoint
5. Тествай с малко плащане

---

**Готово!** 🎉 Сега Stripe трябва да работи в твоето приложение.

