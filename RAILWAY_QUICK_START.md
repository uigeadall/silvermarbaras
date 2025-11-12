# 🚂 Railway Quick Start - Стъпка по Стъпка

## ✅ Какво е готово

- ✅ `Dockerfile` - готов за Railway
- ✅ `entrypoint.sh` - автоматични миграции
- ✅ `requirements.txt` - всички зависимости
- ✅ `.env.example` - template за environment variables
- ✅ Кодът е в GitHub

---

## 🚀 Deployment на Railway

### Стъпка 1: Регистрация в Railway

1. Отиди на [railway.app](https://railway.app/)
2. Click **"Start a New Project"** или **"Login"**
3. Sign up с **GitHub** (най-лесно)
4. Authorize Railway да достъпи твоите repos

### Стъпка 2: Създай Нов Проект

1. В Railway Dashboard → **"New Project"**
2. Избери **"Deploy from GitHub repo"**
3. Намери и избери repo: `uigeadall/marbaras123`
4. Railway автоматично детектира `Dockerfile`! ✅

### Стъпка 3: Добави Database

1. В проекта → **"New"** → **"Database"** → **"MySQL"** (или **"PostgreSQL"**)
2. Railway автоматично създава database
3. Railway автоматично добавя database environment variables!

**За PostgreSQL (препоръчително):**
- Railway добавя `DATABASE_URL` автоматично

**За MySQL:**
- Railway добавя `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_PORT`

### Стъпка 4: Настрой Environment Variables

1. В проекта → Click на твоя **Service** (web service)
2. Отиди на **"Variables"** tab
3. Добави следните environment variables:

#### Критични:
```env
DJANGO_SECRET_KEY=твоят-генериран-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*.railway.app,твоят-custom-domain.com
```

**Генерирай SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Database (автоматично добавен от Railway):
- `DATABASE_URL` - за PostgreSQL (автоматично)
- ИЛИ `MYSQL_HOST`, `MYSQL_USER`, etc. - за MySQL (автоматично)

#### Stripe:
```env
STRIPE_SECRET_KEY=sk_live_твоят-key
STRIPE_PUBLISHABLE_KEY=pk_live_твоят-key
STRIPE_WEBHOOK_SECRET=whsec_твоят-secret
```

#### Email:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=твоят-sendgrid-api-key
DEFAULT_FROM_EMAIL=sales@marbaras.com
ADMIN_EMAIL=admin@marbaras.com
```

#### Други:
```env
DJANGO_SITE_ID=1
```

### Стъпка 5: Deploy!

Railway автоматично:
- ✅ Build Docker image
- ✅ Deploy приложението
- ✅ Настрой SSL
- ✅ Стартира сървъра

Следи deployment в **"Deployments"** tab.

### Стъпка 6: Миграции и Superuser

Миграциите се изпълняват автоматично при стартиране (entrypoint.sh)!

**Ако искаш да създадеш superuser ръчно:**

1. В Railway Dashboard → Service → **"View Logs"**
2. Click **"Shell"** tab (или "Open Shell")
3. Изпълни:
```bash
python manage.py createsuperuser
```

### Стъпка 7: Проверка

1. Railway автоматично дава URL: `https://your-app.railway.app`
2. Провери health endpoint: `https://your-app.railway.app/health/`
3. Трябва да видиш:
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok"
  }
}
```

---

## 🔧 Настройки

### Custom Domain (Опционално)

1. В Service → **"Settings"** → **"Domains"**
2. Click **"Custom Domain"**
3. Добави твоя domain
4. Railway автоматично настройва SSL!

### Environment Variables

Railway автоматично предоставя:
- Database credentials (като `DATABASE_URL` или MySQL variables)
- Service URL
- Port

Ти трябва да добавиш само:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- Stripe keys
- Email settings

---

## 📊 Monitoring

### Logs

1. Service → **"View Logs"**
2. Виждаш всички logs в реално време
3. Можеш да филтрираш по level

### Metrics

1. Service → **"Metrics"**
2. Виждаш CPU, Memory, Network usage

---

## 🆘 Troubleshooting

### Проблем: Build failed

**Решение:**
- Провери logs за конкретни грешки
- Убеди се че `Dockerfile` е правилен
- Провери дали всички dependencies са в `requirements.txt`

### Проблем: Database connection failed

**Решение:**
- Убеди се че database service е свързан
- Провери environment variables
- Провери дали database service е "Running"

### Проблем: Static files не се показват

**Решение:**
- `collectstatic` се изпълнява автоматично (entrypoint.sh)
- Провери logs дали е успешен
- Провери `STATIC_ROOT` настройка

---

## 💰 Цена

Railway pricing:
- **Free tier:** $5 кредит/месец (за тестване)
- **Starter:** $5/месец (за production)
- **Developer:** $20/месец (за по-големи проекти)

---

## ✅ Checklist

- [ ] Регистриран в Railway
- [ ] Създаден проект от GitHub repo
- [ ] Добавен database (MySQL или PostgreSQL)
- [ ] Добавени environment variables
- [ ] Deployment е успешен
- [ ] Health endpoint работи
- [ ] Създаден superuser (ако е нужно)
- [ ] Тествано приложението

---

## 🎉 Готово!

След като направиш тези стъпки, приложението ти ще е live на Railway! 🚀

---

**Следваща стъпка:** Регистрирай се в Railway и следвай инструкциите! 

