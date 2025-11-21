# ✅ Stripe Setup Checklist

## Текущо състояние:
- ✅ Apple Pay и Google Pay бутони са добавени в checkout страницата
- ✅ Stripe Payment Request Button API е имплементиран
- ✅ Stripe API keys се почистват автоматично (премахват се whitespace и newlines)

## Проверка на Stripe конфигурация:

### 1. Railway Environment Variables

Провери дали имаш следните променливи в Railway → Settings → Variables:

- `STRIPE_SECRET_KEY` - Secret key от Stripe Dashboard (започва с `sk_test_` или `sk_live_`)
- `STRIPE_PUBLISHABLE_KEY` - Publishable key от Stripe Dashboard (започва с `pk_test_` или `pk_live_`)
- `STRIPE_WEBHOOK_SECRET` - Webhook secret от Stripe Dashboard (започва с `whsec_`)

### 2. Stripe Dashboard настройки

1. **API Keys:**
   - Отиди на Stripe Dashboard → Developers → API keys
   - Убеди се че използваш правилните keys (test или live)
   - Копирай keys точно без допълнителни интервали

2. **Webhooks:**
   - Отиди на Stripe Dashboard → Developers → Webhooks
   - Добави endpoint: `https://www.marbaras.com/stripe/webhook/` (или Railway URL)
   - Избери events: `payment_intent.succeeded`, `payment_intent.payment_failed`
   - Копирай webhook secret и го добави в Railway като `STRIPE_WEBHOOK_SECRET`

3. **Apple Pay:**
   - Отиди на Stripe Dashboard → Settings → Payment methods
   - Убеди се че Apple Pay е активиран
   - Добави domain: `www.marbaras.com` (и `marbaras.com` ако работи)
   - Свали и качи Apple Pay certificate (ако е необходимо)

4. **Google Pay:**
   - Отиди на Stripe Dashboard → Settings → Payment methods
   - Убеди се че Google Pay е активиран
   - Добави domain: `www.marbaras.com` (и `marbaras.com` ако работи)

### 3. Проверка на функционалността

1. **Test Mode:**
   - Използвай test keys (`sk_test_` и `pk_test_`)
   - Тествай с test карта: `4242 4242 4242 4242`
   - Expiry: всяка бъдеща дата
   - CVC: всяка 3 цифри

2. **Apple Pay / Google Pay:**
   - Бутоните се появяват автоматично ако:
     - Устройството поддържа Apple Pay/Google Pay
     - Сайтът е на HTTPS (production)
     - Domain-ът е добавен в Stripe Dashboard
   - На localhost или HTTP няма да се появят бутоните

### 4. Production Checklist

Преди да преминеш на live mode:

- [ ] Убеди се че използваш live keys (`sk_live_` и `pk_live_`)
- [ ] Добави production domain в Stripe Dashboard
- [ ] Тествай с реална карта (малка сума)
- [ ] Провери webhook events в Stripe Dashboard
- [ ] Убеди се че email notifications работят

## Важно:

- ⚠️ НЕ споделяй secret keys публично
- ⚠️ Използвай test keys за development
- ⚠️ Премини на live keys само когато си готов за production
- ⚠️ Apple Pay/Google Pay работят само на HTTPS (production)
- ⚠️ Domain-ът трябва да е добавен в Stripe Dashboard за Apple Pay/Google Pay

## Ако бутоните не се появяват:

1. Провери че сайтът е на HTTPS (production)
2. Провери че domain-ът е добавен в Stripe Dashboard
3. Провери browser console за грешки
4. Убеди се че устройството поддържа Apple Pay/Google Pay
5. Провери че използваш правилните Stripe keys

