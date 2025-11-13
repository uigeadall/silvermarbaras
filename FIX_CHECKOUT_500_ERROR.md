# 🔧 Поправи 500 Грешка при Checkout

## Проблем
При кликване на "Proceed to Checkout" се получава 500 грешка.

## Причина
Най-вероятно Stripe ключовете не са конфигурирани в Railway environment variables.

## Решение: Конфигурирай Stripe в Railway

### Стъпка 1: Вземи Stripe ключовете

1. Отиди на Stripe Dashboard: https://dashboard.stripe.com/
2. Login с твоя Stripe акаунт
3. Отиди на **"Developers"** → **"API keys"**
4. Копирай:
   - **Publishable key** (за frontend)
   - **Secret key** (за backend)

### Стъпка 2: Добави ключовете в Railway

1. Отиди на Railway Dashboard: https://railway.app/dashboard
2. Избери проект: **hearty-optimism**
3. Избери service: **marbaras**
4. Отиди на таба **"Variables"**
5. Добави следните environment variables:

```
STRIPE_SECRET_KEY=sk_test_... (или sk_live_... за production)
STRIPE_PUBLISHABLE_KEY=pk_test_... (или pk_live_... за production)
STRIPE_WEBHOOK_SECRET=whsec_... (опционално, за webhooks)
```

### Стъпка 3: Redeploy

1. След като добавиш environment variables, Railway автоматично ще redeploy-не приложението
2. Изчакай деплоя да завърши (1-2 минути)

### Стъпка 4: Провери

1. Отвори приложението: https://marbaras-production.up.railway.app
2. Добави продукт в количката
3. Кликни на "Proceed to Checkout"
4. Провери дали работи без 500 грешка

---

## Алтернатива: Ако нямаш Stripe акаунт

Ако нямаш Stripe акаунт или не искаш да го използваш засега:

1. Можеш да използваш **test keys** от Stripe:
   - Publishable key: `pk_test_51...`
   - Secret key: `sk_test_51...`

2. Или можеш да деактивираш Stripe временно (не препоръчително за production)

---

## Проверка на логовете

Ако все още има проблеми, провери логовете:

1. Railway Dashboard → `marbaras` service → **"Logs"** tab
2. Търси за грешки свързани с:
   - `Stripe PaymentIntent creation failed`
   - `Stripe secret key is not configured`
   - `500 Internal Server Error`

---

## Следващи стъпки

Сподели:
1. Имаш ли Stripe акаунт?
2. Добави ли Stripe ключовете в Railway Variables?
3. Работи ли checkout сега?

