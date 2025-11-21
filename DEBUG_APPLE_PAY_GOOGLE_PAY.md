# 🔍 Debug Apple Pay / Google Pay

## Проверка защо бутоните не се появяват:

### 1. Провери Browser Console

1. Отвори checkout страницата
2. Натисни F12 (или Cmd+Option+I на Mac) за Developer Tools
3. Отиди на "Console" tab
4. Търси съобщения които започват с "===" или "✅" или "❌"

**Какво да търсиш:**
- `=== Payment Request Check ===` - показва дали Payment Request е наличен
- `✅ Payment Request is available!` - означава че е наличен
- `❌ Payment Request not available` - означава че не е наличен

### 2. Проверки:

#### A. HTTPS
- Бутоните работят само на HTTPS
- Провери в console: `Is HTTPS: true` или `false`
- Ако е `false`, това е проблемът

#### B. Domain в Stripe Dashboard
1. Отиди на Stripe Dashboard → Settings → Payment methods
2. Кликни на "Apple Pay"
3. Провери дали `www.marbaras.com` е добавен в "Domains"
4. Кликни на "Google Pay"
5. Провери дали `www.marbaras.com` е добавен в "Domains"

#### C. Stripe Keys
1. Провери Railway → Settings → Variables
2. Убеди се че имаш:
   - `STRIPE_PUBLISHABLE_KEY` = `pk_live_...` (live key)
   - `STRIPE_SECRET_KEY` = `sk_live_...` (live key)
3. Убеди се че keys са правилно копирани (без допълнителни интервали)

#### D. Device Support
- Apple Pay работи само на:
  - iPhone/iPad с Safari
  - Mac с Safari и Touch ID/Face ID
- Google Pay работи само на:
  - Android устройства с Chrome
  - Desktop Chrome (с Google Pay настройки)

### 3. Често срещани проблеми:

#### Проблем 1: Domain не е добавен в Stripe
**Решение:** Добави `www.marbaras.com` в Stripe Dashboard → Settings → Payment methods → Apple Pay/Google Pay → Domains

#### Проблем 2: Не е на HTTPS
**Решение:** Убеди се че сайтът е на `https://www.marbaras.com` (не `http://`)

#### Проблем 3: Test keys вместо Live keys
**Решение:** Убеди се че използваш `pk_live_` и `sk_live_` keys (не `pk_test_` и `sk_test_`)

#### Проблем 4: Устройството не поддържа Apple Pay/Google Pay
**Решение:** Тествай на устройство което поддържа (iPhone за Apple Pay, Android за Google Pay)

### 4. Как да тестваш:

1. **На iPhone/iPad:**
   - Отвори `https://www.marbaras.com` в Safari
   - Отиди на checkout страницата
   - Трябва да видиш Apple Pay бутон

2. **На Android:**
   - Отвори `https://www.marbaras.com` в Chrome
   - Отиди на checkout страницата
   - Трябва да видиш Google Pay бутон

3. **На Desktop:**
   - Apple Pay: Safari на Mac с Touch ID/Face ID
   - Google Pay: Chrome с Google Pay настройки

### 5. Проверка в Console:

След като отвориш checkout страницата, в console трябва да видиш:

```
=== Creating Payment Request ===
Total amount: [сума]
Total in cents: [сума в центове]
Currency: USD
Country: BG (Bulgaria)
✅ Payment Request object created
=== Payment Request Check ===
Payment Request available: [обект или null]
```

**Ако виждаш `null`:**
- Провери дали domain е добавен в Stripe
- Провери дали е на HTTPS
- Провери дали устройството поддържа Apple Pay/Google Pay

**Ако виждаш обект:**
- Бутонът трябва да се появи автоматично
- Ако не се появява, провери за JavaScript грешки в console

### 6. Ако все още не работи:

1. Провери Railway logs за грешки
2. Провери browser console за JavaScript грешки
3. Убеди се че Stripe keys са правилно конфигурирани
4. Провери дали domain е правилно добавен в Stripe Dashboard

