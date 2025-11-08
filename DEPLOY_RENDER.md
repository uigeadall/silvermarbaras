# 🎨 Render Deployment Guide - Стъпка по Стъпка

## 🎯 Защо Render?

- ✅ Автоматично детектира Dockerfile
- ✅ Автоматичен SSL
- ✅ Git-based deployment
- ✅ Managed PostgreSQL/MySQL
- ✅ Добра цена ($7-25/месец)
- ✅ Много лесно!

---

## 🚀 Стъпка по Стъпка Deployment

### Стъпка 1: Подготви Code за GitHub

```bash
# Провери дали всичко е готово
ls -la Dockerfile docker-compose.yml .env.example

# Ако нямаш .gitignore, създай го
# (вече е създаден)

# Commit всички промени
git add .
git commit -m "Add Docker support for Render deployment"
git push origin main
```

### Стъпка 2: Регистрация в Render

1. Отиди на [render.com](https://render.com/)
2. Click "Get Started for Free"
3. Sign up с GitHub (най-лесно)
4. Authorize Render да достъпи твоите repos

### Стъпка 3: Създай Web Service

1. В Render Dashboard → "New +"
2. Избери "Web Service"
3. Connect твоя GitHub repo
4. Render автоматично детектира `Dockerfile`! ✅

### Стъпка 4: Настрой Web Service

**Basic Settings:**
- **Name:** `marbaras` (или каквото искаш)
- **Region:** Избери най-близкия (EU или US)
- **Branch:** `main` (или твоя branch)
- **Root Directory:** `.` (остави празно)
- **Runtime:** `Docker` (Render автоматично го избира)

**Build & Deploy:**
- **Build Command:** (остави празно - Dockerfile се използва)
- **Start Command:** (остави празно - Dockerfile CMD се използва)

### Стъпка 5: Добави PostgreSQL Database

1. В Render Dashboard → "New +"
2. Избери "PostgreSQL" (или "MySQL" ако предпочиташ)
3. Настройки:
   - **Name:** `marbaras-db`
   - **Database:** `marbaras`
   - **User:** (Render автоматично генерира)
   - **Region:** Същия като web service
4. Click "Create Database"
5. **Копирай connection string!** (ще ти трябва)

### Стъпка 6: Настрой Environment Variables

В Web Service → Environment, добави:

#### Критични:
```env
DJANGO_SECRET_KEY=твоят-генериран-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=твоят-app.onrender.com,*.onrender.com
```

#### Database (от Render PostgreSQL):
```env
MYSQL_DATABASE=твоят-database-name
MYSQL_USER=твоят-database-user
MYSQL_PASSWORD=твоят-database-password
MYSQL_HOST=твоят-database-host.onrender.com
MYSQL_PORT=3306
```

**Или ако използваш PostgreSQL:**
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

#### Stripe:
```env
STRIPE_SECRET_KEY=sk_test_твоят-key
STRIPE_PUBLISHABLE_KEY=pk_test_твоят-key
STRIPE_WEBHOOK_SECRET=whsec_твоят-secret
```

#### Email:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=твоят-email@gmail.com
EMAIL_HOST_PASSWORD=твоят-app-password
DEFAULT_FROM_EMAIL=sales@marbaras.com
ADMIN_EMAIL=admin@marbaras.com
```

#### Други:
```env
DJANGO_SITE_ID=1
```

### Стъпка 7: Link Database към Web Service

1. В Web Service → "Connections"
2. Click "Connect" до твоя database
3. Render автоматично добавя database environment variables!

### Стъпка 8: Deploy!

1. Click "Save Changes"
2. Render автоматично:
   - Build Docker image
   - Deploy приложението
   - Настрой SSL
   - Стартира сървъра

3. Следи deployment в "Events" tab
4. Когато е готово, ще видиш: "Your service is live at https://..."

### Стъпка 9: Миграции и Superuser

1. В Web Service → "Shell"
2. Изпълни:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## ✅ Проверка

1. Отиди на твоя Render URL: `https://твоят-app.onrender.com`
2. Провери health: `https://твоят-app.onrender.com/health/`
3. Тествай admin: `https://твоят-app.onrender.com/admin/`

---

## 🔧 Render Специфични Настройки

### Custom Domain (Опционално)

1. Settings → Custom Domains
2. Добави твоя domain
3. Render автоматично настройва SSL!

### Environment Variables от Database

Render автоматично предоставя:
- `DATABASE_URL` (за PostgreSQL)
- Или отделни променливи за MySQL

**Ако искаш да използваш DATABASE_URL:**

В `settings.py` можеш да добавиш:
```python
import os
import dj_database_url

# Render provides DATABASE_URL
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])
```

### Static Files

Render автоматично serve-ва static files от `STATIC_ROOT`.

Убеди се че в `settings.py`:
```python
STATIC_ROOT = BASE_DIR / "staticfiles"
```

---

## 💰 Цена

- **Free Tier:** 
  - Web Service спира след 15 минути неактивност
  - Подходящо за тестване
  
- **Starter Plan:** $7/месец
  - Always-on
  - 512MB RAM
  - Подходящо за малки проекти

- **Standard Plan:** $25/месец
  - Always-on
  - 2GB RAM
  - Подходящо за средни проекти

**Database:** Включено в плана или отделно ($7/месец)

---

## 🆘 Troubleshooting

### Проблем: Build failed

**Решение:**
1. Провери logs в Render Dashboard → "Logs"
2. Убеди се че `Dockerfile` е правилен
3. Провери дали всички dependencies са в `requirements.txt`
4. Провери дали `Dockerfile` е в root директорията

### Проблем: Database connection failed

**Решение:**
1. Провери environment variables
2. Убеди се че database е linked
3. Провери database credentials в Render Dashboard
4. Ако използваш PostgreSQL, провери `DATABASE_URL`

### Проблем: Static files не се показват

**Решение:**
1. Убеди се че `collectstatic` се изпълнява
2. Провери `STATIC_ROOT` настройка
3. Провери Render logs

### Проблем: Service спира след 15 минути (Free tier)

**Решение:**
- Upgrade към Starter plan ($7/месец)
- Или използвай UptimeRobot/Pingdom да ping-ва `/health/` всеки 10 минути

---

## 🔄 Auto-Deploy

Render автоматично deploy-ва при:
- Push в main branch
- Manual deploy от dashboard

Можеш да disable auto-deploy в Settings → "Auto-Deploy"

---

## 📊 Monitoring

Render предоставя:
- **Logs:** Real-time logs в dashboard
- **Metrics:** CPU, Memory, Request count
- **Events:** Deployment history

---

## 🔐 Security

- ✅ Автоматичен SSL (HTTPS)
- ✅ Environment variables са encrypted
- ✅ Database connections са secure
- ✅ Security headers (от Django settings)

---

## 📚 Допълнителни Ресурси

- [Render Documentation](https://render.com/docs)
- `DEPLOY_DOCKER.md` - за общи Docker инструкции
- `HOSTING_OPTIONS.md` - за други hosting опции

---

## ✅ Checklist

- [ ] Code е в GitHub
- [ ] Dockerfile е готов
- [ ] Render account създаден
- [ ] Web Service създаден
- [ ] Database създаден и linked
- [ ] Environment variables добавени
- [ ] Deploy успешен
- [ ] Миграции приложени
- [ ] Superuser създаден
- [ ] Static files събрани
- [ ] Health endpoint работи
- [ ] Custom domain (опционално)

---

**Следваща стъпка:** Push в GitHub и следвай стъпките! 🚀

