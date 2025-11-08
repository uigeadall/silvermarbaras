# ⚡ Render Quick Start - 5 Минути

## 🚀 Бързо Deployment

### 1. Push в GitHub (ако не е направено)

```bash
# Провери статус
git status

# Добави всички файлове
git add .

# Commit
git commit -m "Ready for Render deployment"

# Push
git push origin main
```

### 2. Render Setup (2 минути)

1. Отиди на [render.com](https://render.com/)
2. Sign up с GitHub
3. "New +" → "Web Service"
4. Connect твоя repo
5. Render автоматично детектира Dockerfile! ✅

### 3. Настройки (1 минута)

**Basic:**
- Name: `marbaras`
- Region: Избери най-близкия
- Branch: `main`

**Environment Variables:**
Кликни "Add Environment Variable" и добави:

```env
DJANGO_SECRET_KEY=генерирай-нов-ключ
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=твоят-app.onrender.com,*.onrender.com
```

### 4. Database (1 минута)

1. "New +" → "PostgreSQL" (или MySQL)
2. Name: `marbaras-db`
3. Click "Create"
4. В Web Service → "Connections" → "Connect" database

### 5. Deploy! (1 минута)

1. Click "Save Changes"
2. Render автоматично deploy-ва!
3. Следи в "Events" tab
4. Когато е готово → "Your service is live at..."

### 6. Миграции

1. Web Service → "Shell"
2. Изпълни:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## ✅ Готово!

Твоя сайт е live на: `https://твоят-app.onrender.com`

---

## 🔧 Следващи Стъпки

1. Добави останалите environment variables (Stripe, Email)
2. Настрой custom domain (опционално)
3. Upgrade към Starter plan за always-on ($7/месец)

---

Виж `DEPLOY_RENDER.md` за пълни инструкции! 📚

