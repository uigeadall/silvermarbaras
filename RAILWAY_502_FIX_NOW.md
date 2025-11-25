# 🔧 Railway 502 Bad Gateway Fix

## Проблем

Виждаш "502 Bad Gateway" - приложението не отговаря.

---

## Стъпка 1: Провери Deploy Logs

1. В Railway Dashboard → `marbaras` service
2. Отиди на **"Deploy Logs"** tab
3. Търси за:
   - ❌ "Database connection failed"
   - ❌ "Migration failed"
   - ❌ "Gunicorn failed to start"
   - ❌ "Can't connect to MySQL"
   - ❌ "OperationalError"

**Сподели какво виждаш в Deploy Logs!**

---

## Стъпка 2: Провери HTTP Logs

1. В Railway Dashboard → `marbaras` service
2. Отиди на **"HTTP Logs"** tab
3. Търси за грешки или warnings

---

## Стъпка 3: Провери Database Connection

### Проверка 1: DATABASE_URL

1. Кликни на `marbaras` service → Variables tab
2. Провери `DATABASE_URL`:
   - Трябва да започва с `mysql://`
   - Не трябва да е празен
   - Трябва да съдържа `mysql.railway.internal`

### Проверка 2: MySQL Service

1. В Architecture view, кликни на `MySQL` service
2. Провери статуса:
   - Трябва да е "Active" (зелена галочка)
   - Ако не е Active → изчакай да стане Active

---

## Често Срещани Причини

### Причина 1: Database Connection Failed

**Симптоми:**
- "Database is unavailable - retry X/30..."
- "Can't connect to MySQL server"
- "OperationalError"

**Решение:**
1. Провери дали MySQL service е Active
2. Провери `DATABASE_URL` в Variables
3. Провери дали има линия между `marbaras` и `MySQL`

### Причина 2: Migration Failed

**Симптоми:**
- "Migration failed"
- "django.db.utils.OperationalError"

**Решение:**
1. Провери Deploy Logs за конкретни грешки
2. Опитай да приложиш миграциите ръчно:
   ```bash
   railway run python manage.py migrate
   ```

### Причина 3: Gunicorn Failed to Start

**Симптоми:**
- "Starting Gunicorn..." но не продължава
- "Booting worker..." но не продължава

**Решение:**
1. Провери Deploy Logs за конкретни грешки
2. Провери дали `PORT` environment variable е настроен
3. Провери дали има грешки в application code

---

## Стъпка 4: Провери Application Logs

1. В Railway Dashboard → `marbaras` service
2. Отиди на **"Logs"** tab (не Deploy Logs)
3. Търси за:
   - Application errors
   - Database errors
   - Python exceptions

---

## Стъпка 5: Redeploy (Ако нищо не работи)

1. Кликни на `marbaras` service → Deployments
2. Кликни "Redeploy"
3. Изчакай deploy-а да завърши
4. Провери Deploy Logs отново

---

## Какво да направиш сега

1. ⚠️ Провери Deploy Logs - какво виждаш там?
2. ⚠️ Провери HTTP Logs - има ли грешки?
3. ⚠️ Провери Database Connection - MySQL Active ли е?
4. ⚠️ Сподели логовете тук за да видим какъв е проблемът

---

## Резюме

1. Провери Deploy Logs за грешки
2. Провери HTTP Logs
3. Провери Database Connection
4. Сподели логовете за debugging

---

**Сподели какво виждаш в Deploy Logs - какви са грешките?**

