# Настройка за Реални Имейли

## Текущо Състояние

В момента използваш **Mailtrap Sandbox**, което означава:
- ✅ Имейлите се изпращат успешно
- ❌ НО не стигат до реални email адреси
- ✅ Виждаш ги в Mailtrap inbox (за тестване)

## За да получаваш РЕАЛНИ имейли

Трябва да смениш email backend от Mailtrap sandbox към реален SMTP сървър.

### Вариант 1: Gmail (Най-лесно)

1. **Създай App Password в Google:**
   - Отиди в [Google Account](https://myaccount.google.com/)
   - Security → 2-Step Verification (трябва да е включено)
   - App passwords → Generate
   - Копирай генерирания парола

2. **Добави в `.env` файла:**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=sales@marbaras.com
```

3. **Рестартирай сървъра**

### Вариант 2: SendGrid (Препоръчано за production)

1. Регистрирай се на [SendGrid](https://sendgrid.com/) (безплатен план до 100 имейла/ден)

2. Създай API Key:
   - Settings → API Keys → Create API Key
   - Копирай API ключа

3. **Добави в `.env`:**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=sales@marbaras.com
```

### Вариант 3: Mailgun (Добър за production)

1. Регистрирай се на [Mailgun](https://www.mailgun.com/)

2. **Добави в `.env`:**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=sales@marbaras.com
```

## Тестване

След като настроиш реален SMTP:

```bash
# Тествай с твоя реален email
python3 manage.py test_emails --email your-real-email@gmail.com --type order
```

Или направи тестова поръчка - ще получиш email!

## Важно!

- **Gmail:** Използвай App Password, НЕ обикновената парола
- **SendGrid/Mailgun:** По-добри за production, по-надеждни
- **Mailtrap:** Остави го за development/тестване

## Проверка

След настройка, провери:

```bash
python3 manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'sales@marbaras.com', ['your-email@gmail.com'])
```

Ако получиш email - всичко работи! 🎉

