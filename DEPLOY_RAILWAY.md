# 🚂 Railway Deployment Guide (Най-лесно с Docker)

## 🎯 Защо Railway?

- ✅ Автоматично детектира Dockerfile
- ✅ Автоматичен SSL
- ✅ Git-based deployment
- ✅ Managed MySQL database
- ✅ Добра цена ($5-20/месец)
- ✅ Много лесно!

---

## 🚀 Стъпка по Стъпка

### Стъпка 1: Подготви Code

1. Убеди се че имаш:
   - ✅ `Dockerfile`
   - ✅ `requirements.txt`
   - ✅ `.env.example`
   - ✅ `.dockerignore`

2. Push в GitHub:
```bash
git add .
git commit -m "Add Docker support"
git push origin main
```

### Стъпка 2: Регистрация в Railway

1. Отиди на [railway.app](https://railway.app/)
2. Sign up с GitHub
3. Authorize Railway да достъпи твоите repos

### Стъпка 3: Създай Нов Проект

1. Click "New Project"
2. "Deploy from GitHub repo"
3. Избери твоя repo
4. Railway автоматично детектира Dockerfile!

### Стъпка 4: Добави Database

1. В проекта → "New" → "Database" → "MySQL"
2. Railway автоматично създава database
3. Копирай connection string

### Стъпка 5: Настрой Environment Variables

В Railway dashboard → Variables, добави:

```env
DJANGO_SECRET_KEY=твоят-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=твоят-domain.railway.app,*.railway.app
MYSQL_DATABASE=railway
MYSQL_USER=root
MYSQL_PASSWORD=от-railway-database
MYSQL_HOST=от-railway-database
MYSQL_PORT=3306
STRIPE_SECRET_KEY=твоят-stripe-key
STRIPE_PUBLISHABLE_KEY=твоят-stripe-key
STRIPE_WEBHOOK_SECRET=твоят-webhook-secret
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=твоят-email
EMAIL_HOST_PASSWORD=твоят-password
DEFAULT_FROM_EMAIL=sales@marbaras.com
```

**Важно:** Railway автоматично предоставя database credentials като environment variables!

### Стъпка 6: Настрой Custom Domain (Опционално)

1. Settings → Domains → "Custom Domain"
2. Добави твоя domain
3. Railway автоматично настройва SSL!

### Стъпка 7: Deploy!

Railway автоматично:
- Build Docker image
- Deploy приложението
- Настрой SSL
- Стартира сървъра

### Стъпка 8: Миграции и Superuser

1. В Railway dashboard → Deployments → Latest
2. Click "View Logs"
3. Отвори "Shell" tab
4. Изпълни:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## ✅ Проверка

1. Отиди на твоя Railway URL: `https://твоят-проект.railway.app`
2. Провери health: `https://твоят-проект.railway.app/health/`
3. Тествай admin: `https://твоят-проект.railway.app/admin/`

---

## 🔧 Railway Специфични Настройки

### Railway автоматично предоставя:

- `DATABASE_URL` - за database connection
- `RAILWAY_ENVIRONMENT` - за environment detection
- `PORT` - за порт (Railway автоматично мапва)

### Ако искаш да използваш Railway's DATABASE_URL:

В `settings.py` можеш да добавиш:

```python
import os
import dj_database_url

# Railway provides DATABASE_URL
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])
```

---

## 💰 Цена

- **Hobby Plan:** $5/месец (500 hours)
- **Pro Plan:** $20/месец (unlimited)
- **Database:** Включено в плана

---

## 🆘 Troubleshooting

### Проблем: Build failed

**Решение:**
- Провери logs в Railway dashboard
- Убеди се че `Dockerfile` е правилен
- Провери дали всички dependencies са в `requirements.txt`

### Проблем: Database connection failed

**Решение:**
- Провери environment variables
- Убеди се че database service е linked
- Провери database credentials в Railway dashboard

### Проблем: Static files не се показват

**Решение:**
- Убеди се че `collectstatic` се изпълнява
- Провери `STATIC_ROOT` настройка
- Провери Railway logs

---

## 📚 Допълнителни Ресурси

- [Railway Documentation](https://docs.railway.app/)
- `DEPLOY_DOCKER.md` - за общи Docker инструкции
- `HOSTING_OPTIONS.md` - за други hosting опции

---

**Railway е най-лесният начин за deployment с Docker!** 🚀

