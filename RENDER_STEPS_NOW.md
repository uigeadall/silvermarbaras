# 🚀 Render Deployment - Стъпки СЕГА

## ✅ Подготовка (2 минути)

### 1. Commit всички промени

```bash
# Провери какво е променено
git status

# Добави всички файлове
git add .

# Commit
git commit -m "Add Docker support and production improvements"

# Push в GitHub
git push origin newone
```

**Важно:** Убеди се че `.env` файлът НЕ е в git (трябва да е в `.gitignore`)

---

## 🌐 Render Setup (5 минути)

### Стъпка 1: Регистрация

1. Отиди на [render.com](https://render.com/)
2. Click "Get Started for Free"
3. Sign up с GitHub (най-лесно)
4. Authorize Render

### Стъпка 2: Създай Web Service

1. Dashboard → "New +" → "Web Service"
2. "Connect account" → Избери GitHub
3. Избери твоя repo: `МагазинСребро`
4. Click "Connect"

### Стъпка 3: Настрой Web Service

**Basic Settings:**
- **Name:** `marbaras` (или каквото искаш)
- **Region:** `Frankfurt` (EU) или `Oregon` (US) - избери най-близкия
- **Branch:** `newone` (твоя branch)
- **Root Directory:** `.` (остави празно)
- **Runtime:** `Docker` ✅ (Render автоматично го избира!)

**Build & Deploy:**
- **Build Command:** (остави празно)
- **Start Command:** (остави празно)

### Стъпка 4: Environment Variables

Click "Add Environment Variable" и добави:

#### Критични (задължителни):
```
DJANGO_SECRET_KEY=*)i75nj7tp#fpc$%+m#ey7m1#w92_mi!*(6%hdifndk68easj^
```
(Използвай генерирания ключ или генерирай нов)

```
DJANGO_DEBUG=False
```

```
DJANGO_ALLOWED_HOSTS=marbaras.onrender.com,*.onrender.com
```
(Смени `marbaras` с твоя service name)

#### Database (ще добавим след като създадем database):
```
MYSQL_DATABASE=marbaras
MYSQL_USER=...
MYSQL_PASSWORD=...
MYSQL_HOST=...
MYSQL_PORT=3306
```

#### Stripe (добави твоите keys):
```
STRIPE_SECRET_KEY=sk_test_твоят-key
STRIPE_PUBLISHABLE_KEY=pk_test_твоят-key
STRIPE_WEBHOOK_SECRET=whsec_твоят-secret
```

#### Email (добави твоите настройки):
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=твоят-email@gmail.com
EMAIL_HOST_PASSWORD=твоят-app-password
DEFAULT_FROM_EMAIL=sales@marbaras.com
```

#### Други:
```
DJANGO_SITE_ID=1
```

### Стъпка 5: Създай Database

1. Dashboard → "New +" → "PostgreSQL" (или "MySQL")
2. Настройки:
   - **Name:** `marbaras-db`
   - **Database:** `marbaras`
   - **Region:** Същия като web service
3. Click "Create Database"
4. **Копирай connection details!**

### Стъпка 6: Link Database

1. Влез в твоя Web Service
2. Tab "Connections"
3. Click "Connect" до `marbaras-db`
4. Render автоматично добавя database environment variables!

**Ако използваш PostgreSQL:**
Render добавя `DATABASE_URL` автоматично.

**Ако използваш MySQL:**
Добави ръчно в Environment Variables:
```
MYSQL_HOST=от-render-dashboard
MYSQL_USER=от-render-dashboard
MYSQL_PASSWORD=от-render-dashboard
MYSQL_DATABASE=marbaras
MYSQL_PORT=3306
```

### Стъпка 7: Deploy!

1. Click "Save Changes" в Web Service
2. Render автоматично:
   - Build Docker image
   - Deploy приложението
   - Настрой SSL
3. Следи deployment в "Events" tab
4. Когато видиш "Your service is live at..." → готово! ✅

---

## 🔧 След Deployment

### Миграции и Superuser

1. В Web Service → Tab "Shell"
2. Изпълни:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Проверка

1. Отиди на твоя URL: `https://marbaras.onrender.com`
2. Health check: `https://marbaras.onrender.com/health/`
3. Admin: `https://marbaras.onrender.com/admin/`

---

## ⚠️ Важни Бележки

### Free Tier Ограничения:
- Service спира след 15 минути неактивност
- За production upgrade към Starter ($7/месец)

### За Always-On:
1. Settings → Plan → "Starter" ($7/месец)
2. Или използвай UptimeRobot да ping-ва `/health/` всеки 10 минути

### Custom Domain:
1. Settings → Custom Domains
2. Добави твоя domain
3. Render автоматично настройва SSL!

---

## 🆘 При Проблеми

### Build Failed:
- Провери logs в Render Dashboard
- Убеди се че `Dockerfile` е правилен
- Провери дали всички файлове са в GitHub

### Database Connection Failed:
- Провери environment variables
- Убеди се че database е linked
- Провери database credentials

### Service не стартира:
- Провери logs
- Убеди се че `DJANGO_SECRET_KEY` е зададен
- Провери `DJANGO_ALLOWED_HOSTS`

---

## ✅ Checklist

- [ ] Code е push-нат в GitHub
- [ ] Render account създаден
- [ ] Web Service създаден
- [ ] Database създаден и linked
- [ ] Environment variables добавени
- [ ] Deploy успешен
- [ ] Миграции приложени
- [ ] Superuser създаден
- [ ] Static files събрани
- [ ] Health endpoint работи

---

**Следваща стъпка:** Push в GitHub и следвай стъпките! 🚀

