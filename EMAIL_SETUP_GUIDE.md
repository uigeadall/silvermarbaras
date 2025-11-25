# 📧 Ръководство за настройка на автоматични имейли

## Преглед

Системата за автоматични имейли в Marbaras изпраща имейли автоматично при следните събития:

1. **Регистрация** - Welcome email при създаване на нов акаунт
2. **Поръчка** - Order confirmation email при създаване на поръчка
3. **Изпратена поръчка** - Order shipped email (когато администраторът маркира поръчката като изпратена)

## Стъпка 1: Настройка на Email Backend

### Опция A: Gmail (Препоръчано за тестване)

1. Отидете на [Google Account Settings](https://myaccount.google.com/)
2. Отидете на **Security** → **2-Step Verification** (активирайте ако не е)
3. Отидете на **Security** → **App Passwords**
4. Създайте нов App Password за "Mail"
5. Копирайте генерирания парола

### Опция B: Друг SMTP сървър

Използвайте настройките на вашия email provider (SendGrid, Mailgun, AWS SES, и т.н.)

## Стъпка 2: Конфигуриране на .env файл

Създайте `.env` файл в корена на проекта (или копирайте `.env.example`):

```env
# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=sales@marbaras.com
ADMIN_EMAIL=admin@marbaras.com
```

### За Gmail:
- `EMAIL_HOST=smtp.gmail.com`
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `EMAIL_HOST_USER` = вашия Gmail адрес
- `EMAIL_HOST_PASSWORD` = App Password (не обикновения парола!)

### За други SMTP сървъри:

**SendGrid:**
```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

**Mailgun:**
```env
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=your-mailgun-username
EMAIL_HOST_PASSWORD=your-mailgun-password
```

## Стъпка 3: Тестване на имейли

Използвайте management командата за тестване:

```bash
python manage.py test_emails --email your-email@example.com --type all
```

Или тествайте отделни типове:
```bash
# Тестване на welcome email
python manage.py test_emails --email your-email@example.com --type welcome

# Тестване на order confirmation email
python manage.py test_emails --email your-email@example.com --type order

# Тестване на order shipped email
python manage.py test_emails --email your-email@example.com --type shipped
```

## Стъпка 4: Проверка на настройките

Проверете че в `settings.py` имате правилните настройки:

```python
EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", "sandbox.smtp.mailtrap.io")
EMAIL_PORT = int(env("EMAIL_PORT", "2525"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "sales@marbaras.com")
```

## Как работи автоматизацията

### 1. Регистрация

Когато потребител се регистрира (чрез `register_view` или allauth), автоматично се изпраща welcome email:

- **Сигнал:** `user_registered` или `user_signed_up`
- **Файл:** `templates/emails/welcome.html`
- **Функция:** `send_welcome_email()`

### 2. Поръчка

Когато се създаде поръчка (authenticated или guest), автоматично се изпраща order confirmation email:

- **Сигнал:** `order_submitted`
- **Файл:** `templates/emails/order_confirmation.html`
- **Функция:** `send_order_confirmation_email()`

### 3. Изпратена поръчка

Когато администраторът маркира поръчка като изпратена (чрез admin панела), се изпраща order shipped email:

- **Функция:** `send_order_shipped_email()` (извиква се ръчно от admin)

## Troubleshooting

### Имейлите не се изпращат

1. Проверете `.env` файла - всички настройки трябва да са правилни
2. Проверете логовете: `logs/django.log`
3. Тествайте с `test_emails` командата
4. Проверете spam папката

### Gmail грешки

- Уверете се че използвате **App Password**, не обикновения парола
- Проверете че 2-Step Verification е активиран
- Проверете че "Less secure app access" е активиран (ако не използвате App Password)

### Production настройки

За production, препоръчваме:
- **SendGrid** или **Mailgun** за по-надеждно доставяне
- **AWS SES** за голям обем имейли
- Конфигуриране на SPF и DKIM записи

## Допълнителни настройки

### Email Templates

Всички email templates са в `templates/emails/`:
- `welcome.html` / `welcome.txt` - Welcome email
- `order_confirmation.html` / `order_confirmation.txt` - Order confirmation
- `order_shipped.html` / `order_shipped.txt` - Order shipped
- `password_reset.html` / `password_reset.txt` - Password reset

Можете да редактирате тези файлове за да персонализирате имейлите.

### Логове

Всички email грешки се записват в `logs/django.log`. Проверявайте логовете за проблеми.

## Поддръжка

Ако имате проблеми с имейлите, проверете:
1. `.env` файла
2. Логовете (`logs/django.log`)
3. Тествайте с `test_emails` командата
4. Проверете spam папката

