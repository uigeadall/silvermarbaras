# 🚀 Quick Start Guide - Production Setup

## ✅ Текущо Състояние

- ✅ Health endpoint работи: `http://localhost:8000/health/`
- ✅ Database connection: OK
- ✅ Stripe: Configured
- ✅ Cache: OK

## 📝 Стъпка 1: Проверка на .env файла

Твоят `.env` файл съществува. Провери дали имаш всички нужни променливи:

```bash
# Отвори .env файла
nano .env  # или използвай любимия си редактор
```

**Критични променливи:**
- `DJANGO_SECRET_KEY` - трябва да е уникален (не default!)
- `DJANGO_DEBUG` - `True` за development, `False` за production
- `MYSQL_PASSWORD` - твоята MySQL парола
- `STRIPE_SECRET_KEY` - твоя Stripe ключ
- `EMAIL_HOST_USER` - за email изпращане

## 🔐 Стъпка 2: Генерирай SECRET_KEY (ако не е направено)

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Копирай резултата в `.env` файла като:
```
DJANGO_SECRET_KEY=твоят-генериран-ключ-тук
```

## 🧪 Стъпка 3: Тествай Health Endpoint

```bash
# Стартирай сървъра
python3 manage.py runserver

# В друг терминал
curl http://localhost:8000/health/
```

Трябва да видиш:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "checks": {
    "database": "ok",
    "cache": "ok",
    "stripe": "configured"
  }
}
```

## ✅ Стъпка 4: Проверка преди Deployment

```bash
# Провери всичко
python3 manage.py check --deploy

# Събери static files
python3 manage.py collectstatic --noinput

# Провери миграции
python3 manage.py migrate
```

## 📧 Стъпка 5: Настрой Email (за production)

Виж `SETUP_REAL_EMAILS.md` за инструкции.

**Бързо с Gmail:**
1. Отиди в Google Account → Security
2. Включи 2-Step Verification
3. Създай App Password
4. В `.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 💳 Стъпка 6: Настрой Stripe (за production)

1. Отиди в [Stripe Dashboard](https://dashboard.stripe.com)
2. Включи "Live mode"
3. Копирай Live API keys
4. В `.env`:
```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

## 🗄️ Стъпка 7: Database Backup Setup

```bash
# Тествай backup script
chmod +x scripts/backup_db.sh
./scripts/backup_db.sh

# Настрой автоматичен backup (cron)
crontab -e
# Добави:
0 2 * * * /path/to/your/project/scripts/backup_db.sh
```

## 🚀 Стъпка 8: Готов за Deployment!

Когато всичко е готово:

1. Прочети `PRODUCTION_README.md` за пълни инструкции
2. Следвай `NEXT_STEPS.md` за deployment стъпки
3. Използвай `PRODUCTION_CHECKLIST.md` за финална проверка

## 🔍 Бързи Команди

```bash
# Health check
curl http://localhost:8000/health/

# Проверка
python3 manage.py check --deploy

# Static files
python3 manage.py collectstatic --noinput

# Миграции
python3 manage.py migrate

# Логове
tail -f logs/django.log

# Backup
./scripts/backup_db.sh
```

## ⚠️ Важно!

- **НИКОГА** не комитирай `.env` файла в git!
- Винаги използвай `DEBUG=False` в production
- Винаги използвай production Stripe keys в production
- Регулярно прав backup на database

## 🆘 При Проблеми

1. Провери логове: `tail -f logs/django.log`
2. Провери health: `curl http://localhost:8000/health/`
3. Провери database: `python3 manage.py dbshell`
4. Виж `PRODUCTION_README.md` за troubleshooting

---

**Следваща стъпка:** Настрой production email и Stripe keys! 📧💳

