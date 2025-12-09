# Настройка на Email с Jump.bg домейн

Това ръководство обяснява как да настроите автоматично изпращане на имейли чрез вашия email домейн в Jump.bg.

## Автоматични имейли

Системата автоматично изпраща имейли при:

1. **Регистрация на потребител** - Welcome email
2. **Направена поръчка** - Order confirmation email
3. **Забравена парола** - Password reset email

## Настройка в Railway

### 1. Добавете Environment Variables в Railway

Отидете в Railway Dashboard → Вашия проект → Variables и добавете следните променливи:

```bash
# Email Backend (използвайте SMTP за production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Jump.bg SMTP настройки
EMAIL_HOST=mail.jump.bg
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False

# Вашият email адрес и парола от Jump.bg
EMAIL_HOST_USER=support@marbaras.com
EMAIL_HOST_PASSWORD=вашата_парола_тук

# От кой адрес да се изпращат имейлите
DEFAULT_FROM_EMAIL=support@marbaras.com
SERVER_EMAIL=support@marbaras.com

# Admin email за notifications
ADMIN_EMAIL=support@marbaras.com
```

### 2. Важни бележки

- **EMAIL_HOST_USER**: Това трябва да е пълният email адрес (например `support@marbaras.com`)
- **EMAIL_HOST_PASSWORD**: Паролата на email акаунта в Jump.bg
- **EMAIL_PORT**: 
  - `587` за TLS (препоръчително)
  - `465` за SSL (ако 587 не работи, променете `EMAIL_USE_SSL=True` и `EMAIL_USE_TLS=False`)

### 3. Проверка на SPF/DKIM/DMARC записи

За да се гарантира, че имейлите не попадат в spam:

1. Влезте в cPanel на Jump.bg
2. Отидете в "Email Deliverability"
3. Проверете дали SPF и DKIM записите са правилно конфигурирани
4. Добавете DMARC запис ако липсва

## Тестване на имейли

### Вариант 1: Чрез Django команда

```bash
python manage.py test_emails --email ваш_тестов_имейл@example.com --type all
```

### Вариант 2: Чрез браузър (ако имате test_emails view)

Отидете на: `https://www.marbaras.com/test-emails/`

## Проверка на логове

Ако има проблеми с изпращането на имейли, проверете логовете:

```bash
# В Railway Dashboard → Deployments → View Logs
# Или локално:
tail -f logs/django.log
```

## Често срещани проблеми

### Проблем: Имейлите не се изпращат

**Решение:**
1. Проверете дали всички environment variables са правилно зададени в Railway
2. Проверете дали паролата на email акаунта е правилна
3. Проверете дали портът е правилен (587 за TLS или 465 за SSL)
4. Проверете логовете за грешки

### Проблем: Имейлите попадат в spam

**Решение:**
1. Проверете SPF/DKIM/DMARC записите в cPanel
2. Уверете се, че `DEFAULT_FROM_EMAIL` е правилният домейн
3. Използвайте email адрес от вашия домейн (не Gmail/Yahoo и т.н.)

### Проблем: Connection timeout

**Решение:**
1. Проверете дали `EMAIL_HOST` е правилен (`mail.jump.bg` или `smtp.jump.bg`)
2. Опитайте с порт 465 и SSL вместо TLS
3. Проверете дали Railway не блокира изходящите SMTP връзки

## Конфигурация в settings.py

Email настройките вече са конфигурирани в `МагазинСребро/settings.py`:

```python
EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", "mail.jump.bg")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "support@marbaras.com")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "support@marbaras.com")
```

Тези настройки се четат от environment variables, което означава, че можете да ги променяте в Railway без да променяте кода.

## Следващи стъпки

1. Добавете environment variables в Railway
2. Тествайте изпращането на имейли
3. Проверете дали имейлите пристигат правилно
4. Проверете spam папката ако имейлите не се виждат

