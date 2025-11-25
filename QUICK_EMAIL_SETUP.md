# ⚡ Бърз старт за автоматични имейли

## За 5 минути

### 1. Конфигурирайте .env файла

Добавете в `.env` файла:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=sales@marbaras.com
```

**За Gmail:** Създайте App Password от [Google Account Settings](https://myaccount.google.com/apppasswords)

### 2. Тествайте

```bash
python manage.py test_emails --email your-email@example.com
```

### 3. Готово! ✨

Имейлите се изпращат автоматично при:
- ✅ Регистрация на нов потребител
- ✅ Създаване на поръчка

## Проверка

1. Регистрирайте нов потребител → получавате welcome email
2. Направете тестова поръчка → получавате order confirmation email

## Проблеми?

Вижте `EMAIL_SETUP_GUIDE.md` за пълни инструкции и troubleshooting.

