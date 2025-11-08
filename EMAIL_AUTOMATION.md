# Email Automation Guide - Marbaras

## Преглед

Системата за автоматизирани имейли в Marbaras използва Django signals и функции за изпращане на имейли. Всички имейли се изпращат автоматично при определени събития.

## Настройки

### Email Backend

В `settings.py` са конфигурирани следните настройки:

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

### Environment Variables

Добавете в `.env` файла:

```env
# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com  # или вашия SMTP сървър
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=sales@marbaras.com
ADMIN_EMAIL=admin@marbaras.com
```

## Автоматични Имейли

### 1. Welcome Email (Добре дошли)

**Кога се изпраща:**
- При регистрация на нов потребител (чрез `register_view` или allauth)

**Файлове:**
- `templates/emails/welcome.html`
- `templates/emails/welcome.txt`

**Сигнал:** `user_registered` или `user_signed_up` (allauth)

**Функция:** `send_welcome_email(user, base_url)`

### 2. Order Confirmation Email (Потвърждение на поръчка)

**Кога се изпраща:**
- Автоматично при създаване на нова поръчка (чрез `checkout_view` или `guest_checkout_view`)
- Също така изпраща имейл до администратора

**Файлове:**
- `templates/emails/order_confirmation.html`
- `templates/emails/order_confirmation.txt`

**Сигнал:** `order_submitted`

**Функция:** `send_order_confirmation_email(order, base_url, notify_admin=True)`

**Съдържание:**
- Списък с поръчани продукти (включително размери)
- Детайли на поръчката (междинна сума, отстъпка, доставка, общо)
- Адрес за доставка
- Линк за преглед на поръчки

### 3. Order Shipped Email (Поръчката е изпратена)

**Кога се изпраща:**
- Ръчно от Django Admin (чрез admin action)
- Може да се добави автоматизация при промяна на статус на поръчка

**Файлове:**
- `templates/emails/order_shipped.html`
- `templates/emails/order_shipped.txt`

**Функция:** `send_order_shipped_email(order, base_url, tracking_number=None)`

**Как да използвате:**
1. Отидете в Django Admin → Orders
2. Изберете поръчка(и)
3. Изберете action "Изпрати имейл 'Поръчката е изпратена'"
4. Кликнете "Go"

**Съдържание:**
- Информация за доставка
- Tracking номер (ако е предоставен)
- Адрес за доставка
- Списък с продукти

### 4. Password Reset Email (Възстановяване на парола)

**Кога се изпраща:**
- При заявка за възстановяване на парола

**Файлове:**
- `templates/emails/password_reset.html`
- `templates/emails/password_reset.txt`

**Функция:** `send_password_reset_email(user, reset_url, base_url)`

**Забележка:** Django Allauth вече има вградена функционалност за възстановяване на парола. Тази функция може да се използва за кастомна интеграция.

## Ръчно Изпращане на Имейли

### От Python код:

```python
from ecommerce.utils.emailing import (
    send_welcome_email,
    send_order_confirmation_email,
    send_order_shipped_email,
    send_password_reset_email
)
from django.conf import settings

# Welcome email
base_url = "https://marbaras.com"
send_welcome_email(user, base_url)

# Order confirmation
send_order_confirmation_email(order, base_url, notify_admin=True)

# Order shipped
send_order_shipped_email(order, base_url, tracking_number="TRACK123456")

# Password reset
reset_url = f"{base_url}/accounts/password/reset/?token=..."
send_password_reset_email(user, reset_url, base_url)
```

### От Django Admin:

1. **Order Shipped Email:**
   - Admin → Orders → Избери поръчка(и) → Action: "Изпрати имейл 'Поръчката е изпратена'" → Go

## Тестване

### Development (Mailtrap/SMTP Sandbox):

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-mailtrap-user
EMAIL_HOST_PASSWORD=your-mailtrap-password
```

### Console Backend (за тестване):

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Имейлите ще се показват в конзолата вместо да се изпращат.

### File Backend (за тестване):

```env
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/path/to/app-messages
```

Имейлите ще се записват като файлове.

## Подобряване на Templates

Всички email templates са в `templates/emails/`:
- HTML версии (`.html`) - за модерни email клиенти
- Text версии (`.txt`) - за по-стари email клиенти или като fallback

### Структура на Templates:

- Градиентен header с брандинг
- Четливо форматиране
- Responsive дизайн
- Линкове към сайта
- Български език

## Troubleshooting

### Имейлите не се изпращат:

1. Проверете `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` в `.env`
2. Проверете дали SMTP сървърът изисква TLS/SSL
3. Проверете Django logs за грешки
4. Тествайте с `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`

### Имейлите се изпращат, но не пристигат:

1. Проверете SPAM папката
2. Проверете дали `DEFAULT_FROM_EMAIL` е валиден
3. Проверете SPF/DKIM записи за вашия домейн
4. Използвайте email service като SendGrid, Mailgun, или AWS SES

### Gmail специфично:

- Използвайте "App Password" вместо обикновена парола
- Разрешите "Less secure app access" (не се препоръчва)
- Или използвайте OAuth2 (по-сложно)

## Бъдещи Подобрения

- [ ] Добавяне на статус поле в Order модела за автоматизация
- [ ] Автоматично изпращане на "order shipped" email при промяна на статус
- [ ] Email за "order delivered"
- [ ] Email за "abandoned cart" (забравена кошница)
- [ ] Newsletter функционалност
- [ ] Email за промоции и оферти
- [ ] Email за ревюване на продукти след доставка

