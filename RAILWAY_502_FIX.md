# 🔧 Railway 502 Bad Gateway - Fix

## Проблем

Виждаш "502 Bad Gateway" или "Application failed to respond"

**Причина:** Railway не може да се свърже с приложението.

---

## ✅ Решения

### Решение 1: Провери Port Configuration

Railway автоматично предоставя `PORT` environment variable. Трябва да го използваш!

**Проблем:** Gunicorn слуша на порт 8000, но Railway очаква да слушаш на `PORT` environment variable.

**Fix:** Обнови `entrypoint.sh` или `Dockerfile` да използва `PORT` variable.

### Решение 2: Провери Logs

1. В Railway Dashboard → Web Service → "View Logs"
2. Търси за:
   - Database connection errors
   - Port binding errors
   - Application startup errors
   - Import errors

### Решение 3: Провери Environment Variables

1. Web Service → "Variables" tab
2. Убеди се че имаш:
   - `DATABASE_URL` (от database service)
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=*.railway.app`

### Решение 4: Провери Database Connection

1. Убеди се че database service е свързан
2. Провери дали `DATABASE_URL` е правилен
3. Провери logs за database errors

---

## 🔧 Най-често срещани проблеми

### Проблем 1: Port не е правилно конфигуриран

**Симптом:** 502 Bad Gateway

**Решение:** Обнови entrypoint.sh да използва `PORT` environment variable

### Проблем 2: Database connection failed

**Симптом:** Application не стартира

**Решение:** Провери `DATABASE_URL` и database connection

### Проблем 3: Missing environment variables

**Симптом:** Application crash при стартиране

**Решение:** Добави всички нужни environment variables

---

## 📋 Checklist

- [ ] Проверил logs за конкретни грешки
- [ ] Проверил дали `PORT` е използван правилно
- [ ] Проверил database connection
- [ ] Проверил environment variables
- [ ] Проверил дали application стартира успешно

---

**Следваща стъпка:** Провери logs и сподели какво виждаш!

