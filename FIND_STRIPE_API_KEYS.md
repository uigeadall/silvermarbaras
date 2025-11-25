# 🔑 Как да Намериш Stripe API Keys

## Метод 1: Чрез Developers → API

1. В Stripe Dashboard, отиди на **"Developers"** в лявата странична лента
2. Скролни надолу или кликни на **"API"** под "Developers"
3. Там трябва да видиш **"API keys"** секция

## Метод 2: Чрез Settings

1. В Stripe Dashboard, отиди на **"Settings"** (в лявата странична лента)
2. Скролни надолу до **"API"** секция
3. Там трябва да видиш **"API keys"**

## Метод 3: Директна URL

Отиди директно на:
```
https://dashboard.stripe.com/apikeys
```

## Метод 4: Чрез Search

1. Кликни на **"Q Search"** в лявата странична лента
2. Напиши **"API keys"**
3. Кликни на резултата

---

## Какво да търсиш:

След като намериш API keys страницата, ще видиш:

### Test mode keys (за development):
- **Publishable key**: `pk_test_51...` (видим веднага)
- **Secret key**: `sk_test_51...` (кликни "Reveal test key" за да го видиш)

### Live mode keys (за production):
- **Publishable key**: `pk_live_51...` (видим веднага)
- **Secret key**: `sk_live_51...` (кликни "Reveal live key" за да го видиш)

---

## За development/test използвай Test keys!

---

## Алтернатива: Ако все още не можеш да ги намериш

Можеш да създадеш нов API key:

1. Отиди на **"Developers"** → **"API"** → **"API keys"**
2. Кликни на **"Create API key"** или **"+ Create key"**
3. Избери **"Test mode"** за development
4. Копирай новите ключовете

---

## След като намериш ключовете:

1. Копирай **Publishable key** и **Secret key**
2. Отиди на Railway Dashboard → `marbaras` service → **"Variables"**
3. Добави:
   ```
   STRIPE_SECRET_KEY=sk_test_... (копирай Secret key)
   STRIPE_PUBLISHABLE_KEY=pk_test_... (копирай Publishable key)
   ```
4. Railway автоматично ще redeploy-не приложението

---

Сподели какво виждаш в Stripe Dashboard — намери ли API keys или имаш проблем?

