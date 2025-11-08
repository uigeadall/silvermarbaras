# 🧪 Тестване на Email Автоматизация

## Бърз Старт

### 1. Тестване с Console Backend (Най-лесно)

Това ще покаже имейлите в конзолата вместо да ги изпраща:

```bash
# В .env файла или директно в settings.py за тестване
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

След това стартирай сървъра и направи регистрация или поръчка - имейлите ще се покажат в конзолата!

### 2. Тестване с Management Command

Създадохме специален management command за тестване:

```bash
# Тестване на всички имейли
python3 manage.py test_emails --email your-email@example.com

# Тестване само на welcome email
python3 manage.py test_emails --email your-email@example.com --type welcome

# Тестване само на order confirmation
python3 manage.py test_emails --email your-email@example.com --type order

# Тестване само на order shipped
python3 manage.py test_emails --email your-email@example.com --type shipped

# Тестване само на password reset
python3 manage.py test_emails --email your-email@example.com --type reset
```

## Настройки за Различни Сценарии

### Development (Console - за бързо тестване)

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Плюсове:** Моментално виждаш имейлите в конзолата  
**Минуси:** Не изпраща реални имейли

### Development (File Backend - запазва като файлове)

```env
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/tmp/django-emails
```

Създай директорията:
```bash
mkdir -p /tmp/django-emails
```

**Плюсове:** Можеш да отвориш HTML файловете в браузър  
**Минуси:** Трябва да проверяваш файловете ръчно

### Development (Mailtrap - препоръчано)

1. Регистрирай се на [Mailtrap.io](https://mailtrap.io) (безплатно)
2. Създай inbox
3. Копирай SMTP credentials

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-mailtrap-user
EMAIL_HOST_PASSWORD=your-mailtrap-password
DEFAULT_FROM_EMAIL=sales@marbaras.com
```

**Плюсове:** Виждаш имейлите в Mailtrap интерфейса, тестваш HTML/текст версии  
**Минуси:** Изисква регистрация

### Production (Gmail SMTP)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # НЕ обикновената парола!
DEFAULT_FROM_EMAIL=sales@marbaras.com
```

**Важно за Gmail:**
1. Отиди в Google Account → Security
2. Включи "2-Step Verification"
3. Създай "App Password" за Django
4. Използвай App Password като `EMAIL_HOST_PASSWORD`

### Production (SendGrid - препоръчано за production)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=sales@marbaras.com
```

## Стъпка по Стъпка Тестване

### Тест 1: Welcome Email

1. Настрой email backend (console или mailtrap)
2. Стартирай сървъра: `python3 manage.py runserver`
3. Отиди на `/register` и регистрирай нов потребител
4. Провери конзолата/email inbox за welcome email

Или използвай management command:
```bash
python3 manage.py test_emails --email test@example.com --type welcome
```

### Тест 2: Order Confirmation Email

1. Влез в акаунт
2. Добави продукти в кошницата
3. Отиди на checkout и направи поръчка
4. Провери за order confirmation email

Или използвай management command:
```bash
python3 manage.py test_emails --email test@example.com --type order
```

### Тест 3: Order Shipped Email

1. Отиди в Django Admin: `/admin/ecommerce/order/`
2. Избери поръчка
3. Action: "Изпрати имейл 'Поръчката е изпратена'"
4. Кликни "Go"
5. Провери за shipped email

Или използвай management command:
```bash
python3 manage.py test_emails --email test@example.com --type shipped
```

### Тест 4: Password Reset Email

Използвай management command:
```bash
python3 manage.py test_emails --email test@example.com --type reset
```

Или тествай през UI:
1. Отиди на `/accounts/password/reset/`
2. Въведи email
3. Провери за reset email

## Проверка на Резултатите

### Console Backend
Имейлите ще се покажат директно в терминала:
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Welcome to Marbaras ✨
From: sales@marbaras.com
To: test@example.com
Date: ...

Здравейте, test_user,
...
```

### File Backend
Имейлите ще се запазят в `/tmp/django-emails/` (или зададената директория):
```bash
ls -la /tmp/django-emails/
# Ще видиш файлове като: 20250108120000.12345.html
```

Отвори HTML файла в браузър за визуален преглед.

### Mailtrap
1. Влез в Mailtrap dashboard
2. Отиди в твоя inbox
3. Ще видиш всички изпратени имейли
4. Можеш да прегледаш HTML, текст версия, headers, и т.н.

## Troubleshooting

### Имейлите не се показват в конзолата

Провери:
```python
# В Django shell
from django.conf import settings
print(settings.EMAIL_BACKEND)
# Трябва да е: django.core.mail.backends.console.EmailBackend
```

### Грешка при SMTP connection

1. Провери `EMAIL_HOST`, `EMAIL_PORT`
2. Провери `EMAIL_USE_TLS` или `EMAIL_USE_SSL` (обикновено TLS=True, SSL=False)
3. Провери firewall настройки
4. Тествай с `telnet`:
```bash
telnet smtp.gmail.com 587
```

### Gmail "Less secure app" грешка

Използвай App Password вместо обикновена парола:
1. Google Account → Security
2. 2-Step Verification → ON
3. App passwords → Generate
4. Използвай генерирания парола

### Имейлите отиват в SPAM

1. Провери SPAM папката
2. Провери SPF/DKIM записи за домейна
3. Използвай email service като SendGrid/Mailgun за production

## Бърз Тест Script

Създай `test_email_quick.sh`:

```bash
#!/bin/bash
echo "🧪 Тестване на имейли..."
python3 manage.py test_emails --email your-email@example.com --type all
echo "✅ Готово! Провери email inbox."
```

Направи го изпълним:
```bash
chmod +x test_email_quick.sh
./test_email_quick.sh
```

## Production Checklist

Преди да пуснеш в production:

- [ ] Тествал всички типове имейли
- [ ] Проверил HTML версиите в различни email клиенти
- [ ] Проверил текст версиите
- [ ] Настроил правилен SMTP сървър
- [ ] Настроил SPF/DKIM записи
- [ ] Тествал с реални email адреси
- [ ] Проверил spam score
- [ ] Настроил monitoring за failed emails

## Полезни Команди

```bash
# Тестване на всички имейли
python3 manage.py test_emails --email test@example.com

# Проверка на email настройки
python3 manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_BACKEND)
>>> print(settings.EMAIL_HOST)

# Ръчно изпращане на email (в Django shell)
python3 manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

