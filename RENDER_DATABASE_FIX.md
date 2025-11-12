# 🔧 Render Database Connection Fix

## Проблем

При deployment на Render виждаш:
```
Database is unavailable - sleeping
```

## Решения

### ✅ Решение 1: Провери Database Service Connection

1. Отиди в **Render Dashboard**
2. Отвори твоя **Web Service**
3. Отиди на **"Connections"** tab
4. Убеди се че **Database service е свързан**
5. Ако не е свързан, click **"Connect"** до database service-а

### ✅ Решение 2: Провери Environment Variables

В Render Dashboard → Web Service → Environment, провери дали имаш:

**За Render PostgreSQL:**
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

**За съществуваща MySQL база:**
```env
MYSQL_HOST=your-database-host.com
MYSQL_PORT=3306
MYSQL_DATABASE=your_database_name
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
```

### ✅ Решение 3: Провери Database Credentials

1. Отиди в **Database Service** в Render
2. Провери **Internal Database URL** или **Connection String**
3. Копирай го в Web Service Environment Variables като `DATABASE_URL`

### ✅ Решение 4: Render Automatic Database Linking

Ако използваш Render managed database:

1. В **Web Service** → **Connections**
2. Click **"Connect"** до database service-а
3. Render автоматично добавя `DATABASE_URL` environment variable
4. Redeploy web service

### ✅ Решение 5: Провери Database Status

1. Отиди в **Database Service** dashboard
2. Провери дали database е **"Available"**
3. Ако е **"Paused"**, click **"Resume"**

---

## 🔍 Debugging Steps

### Стъпка 1: Провери Logs

В Render Dashboard → Web Service → Logs, виж какви са грешките:
- Connection refused?
- Access denied?
- Timeout?

### Стъпка 2: Провери Database Host

За Render managed databases:
- Използвай **Internal Database URL** (не external!)
- Render автоматично го предоставя когато свържеш database

За external databases:
- Провери дали database host е достъпен от Render
- Може да се наложи да whitelist-неш Render IPs

### Стъпка 3: Тествай Connection Locally

```bash
# Тествай с DATABASE_URL
export DATABASE_URL="postgresql://user:pass@host:5432/db"
python manage.py dbshell
```

---

## 📝 Environment Variables Checklist

Убеди се че имаш всички тези в Render:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-app.onrender.com,*.onrender.com

# Database (избери един от двата)
DATABASE_URL=postgresql://...  # За Render PostgreSQL
# ИЛИ
MYSQL_HOST=...
MYSQL_DATABASE=...
MYSQL_USER=...
MYSQL_PASSWORD=...

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-api-key
```

---

## 🚀 След Fix

1. **Save** environment variables
2. **Redeploy** web service
3. Провери logs дали database connection е успешен
4. Провери health endpoint: `https://your-app.onrender.com/health/`

---

## ⚠️ Важно

- **Render managed databases** изискват database service да е свързан чрез Connections tab
- **External databases** трябва да приемат connections от Render IPs
- **DATABASE_URL** е най-лесният начин за Render

---

**Ако проблемът продължава**, провери Render logs за конкретни database error messages!

