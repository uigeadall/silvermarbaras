# 🔧 Railway 400 Bad Request Fix

## Проблем

Виждаш "400 Bad Request" когато се опитваш да отвориш приложението.

---

## Често Срещани Причини

### Причина 1: ALLOWED_HOSTS не е настроен

**Симптоми:**
- 400 Bad Request
- "DisallowedHost" в логовете

**Решение:**

1. В Railway Dashboard → `marbaras` service → Variables tab
2. Провери `DJANGO_ALLOWED_HOSTS`:
   - Трябва да съдържа: `marbaras-production.up.railway.app`
   - Или: `*` (за development, но не е безопасно за production)

3. Ако няма `DJANGO_ALLOWED_HOSTS`:
   - Кликни "+ New Variable"
   - Име: `DJANGO_ALLOWED_HOSTS`
   - Стойност: `marbaras-production.up.railway.app,localhost,127.0.0.1`

---

### Причина 2: CSRF Token Problem

**Симптоми:**
- 400 Bad Request при POST заявки
- "CSRF verification failed" в логовете

**Решение:**

1. Провери `DJANGO_SECRET_KEY` в Variables:
   - Трябва да е настроен
   - Не трябва да е празен

2. Провери `CSRF_TRUSTED_ORIGINS`:
   - Кликни "+ New Variable"
   - Име: `CSRF_TRUSTED_ORIGINS`
   - Стойност: `https://marbaras-production.up.railway.app`

---

### Причина 3: Static Files Problem

**Симптоми:**
- 400 Bad Request при зареждане на static files
- CSS/JS не се зареждат

**Решение:**

1. Провери дали `STATIC_URL` и `STATIC_ROOT` са правилно настроени
2. Провери дали static files са събрани (виждаш "129 static files copied")

---

### Причина 4: Database Connection Problem

**Симптоми:**
- 400 Bad Request
- Database errors в логовете

**Решение:**

1. Провери `DATABASE_URL` в Variables:
   - Трябва да започва с `mysql://`
   - Трябва да съдържа правилни credentials

2. Провери Deploy Logs за database errors

---

## Стъпка по Стъпка Fix

### Стъпка 1: Провери HTTP Logs

1. В Railway Dashboard → `marbaras` service → HTTP Logs tab
2. Търси за конкретни грешки:
   - "DisallowedHost"
   - "CSRF verification failed"
   - "Database connection error"
   - "Static file not found"

**Сподели какво виждаш в HTTP Logs!**

---

### Стъпка 2: Провери Variables

1. Кликни на `marbaras` service → Variables tab
2. Провери:
   - `DJANGO_ALLOWED_HOSTS` - трябва да съдържа Railway domain
   - `DJANGO_SECRET_KEY` - трябва да е настроен
   - `DATABASE_URL` - трябва да започва с `mysql://`
   - `CSRF_TRUSTED_ORIGINS` - трябва да съдържа Railway domain

---

### Стъпка 3: Добави Липсващи Variables

Ако нямаш `DJANGO_ALLOWED_HOSTS`:

1. Кликни "+ New Variable"
2. Име: `DJANGO_ALLOWED_HOSTS`
3. Стойност: `marbaras-production.up.railway.app,localhost,127.0.0.1`

Ако нямаш `CSRF_TRUSTED_ORIGINS`:

1. Кликни "+ New Variable"
2. Име: `CSRF_TRUSTED_ORIGINS`
3. Стойност: `https://marbaras-production.up.railway.app`

---

### Стъпка 4: Deploy промените

1. В Architecture view, кликни "Deploy"
2. Изчакай deploy-а да завърши
3. Провери приложението отново

---

## Какво да направиш сега

1. ⚠️ Провери HTTP Logs - какво виждаш там?
2. ⚠️ Провери Variables - имаш ли `DJANGO_ALLOWED_HOSTS`?
3. ⚠️ Добави липсващите variables
4. ⚠️ Deploy промените

---

## Резюме

1. Провери HTTP Logs за конкретни грешки
2. Провери Variables за `DJANGO_ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS`
3. Добави липсващите variables
4. Deploy промените

---

**Сподели какво виждаш в HTTP Logs - какви са грешките?**

