# Production Deployment Guide - Marbaras

## 🚀 Production Checklist

### 1. Environment Variables

Копирай `.env.example` към `.env` и попълни всички стойности:

```bash
cp .env.example .env
# Редактирай .env с твоите production стойности
```

**Критични настройки:**
- `DJANGO_SECRET_KEY` - генерирай нов, уникален ключ
- `DJANGO_DEBUG=False` - ВИНАГИ False в production!
- `DJANGO_ALLOWED_HOSTS` - твоите домейни
- `MYSQL_PASSWORD` - силна парола
- `STRIPE_SECRET_KEY` - production ключ (не test!)
- `EMAIL_*` - production SMTP настройки

### 2. Security

✅ **Всички security настройки са автоматично активирани когато `DEBUG=False`:**

- SSL redirect
- Secure cookies
- HSTS headers
- XSS protection
- CSRF protection
- Clickjacking protection

**Допълнителни стъпки:**
- Настрой SSL сертификат (Let's Encrypt)
- Настрой firewall
- Регулярни security updates

### 3. Database

```bash
# Миграции
python3 manage.py migrate

# Създай superuser
python3 manage.py createsuperuser

# Инсталирай timezone таблици (за MySQL)
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql
```

### 4. Static Files

```bash
# Събиране на static files
python3 manage.py collectstatic --noinput

# Настрой nginx/apache да serve-ва static files
```

**Nginx пример:**
```nginx
location /static/ {
    alias /path/to/your/project/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /path/to/your/project/media/;
    expires 7d;
}
```

### 5. WSGI Server

**Gunicorn (препоръчано):**
```bash
pip install gunicorn

# Стартирай
gunicorn МагазинСребро.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

**Systemd service пример:**
```ini
[Unit]
Description=Marbaras Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/venv/bin/gunicorn \
    --access-logfile - \
    --workers 4 \
    --bind unix:/run/gunicorn.sock \
    МагазинСребро.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 6. Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    client_max_body_size 10M;

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /path/to/media/;
        expires 7d;
    }
}
```

### 7. Monitoring

**Health Check Endpoint:**
```
GET /health/
```

Отговор:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T10:00:00Z",
  "checks": {
    "database": "ok",
    "cache": "ok",
    "stripe": "configured"
  }
}
```

**Настрой monitoring service** (UptimeRobot, Pingdom, etc.) да проверява `/health/`

### 8. Logging

Логовете се записват в:
- Console (development)
- `logs/django.log` (production)

**Ротация:** Автоматично, максимум 10MB на файл, 5 backup файла

**Мониторинг:** Настрой Sentry или подобна услуга за error tracking

### 9. Caching (Опционално, но препоръчано)

**Redis:**
```bash
# Инсталирай Redis
sudo apt-get install redis-server

# В .env
REDIS_URL=redis://localhost:6379/0

# В settings.py добави:
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", "redis://127.0.0.1:6379/0"),
    }
}
```

### 10. Database Backups

**Автоматичен backup script:**
```bash
#!/bin/bash
# backup_db.sh
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u root -p$MYSQL_PASSWORD $MYSQL_DATABASE > /backups/marbaras_$DATE.sql
# Запази последните 7 дни
find /backups -name "marbaras_*.sql" -mtime +7 -delete
```

**Cron job:**
```bash
0 2 * * * /path/to/backup_db.sh
```

### 11. Email Configuration

Виж `SETUP_REAL_EMAILS.md` за настройка на production email.

**Препоръчано:** SendGrid или Mailgun за production

### 12. Stripe Webhooks

**Настрой webhook endpoint в Stripe Dashboard:**
- URL: `https://yourdomain.com/webhook/`
- Events: `payment_intent.succeeded`, `payment_intent.payment_failed`
- Secret: Копирай в `STRIPE_WEBHOOK_SECRET`

### 13. Performance Optimization

**Database:**
- Използвай `select_related()` и `prefetch_related()` (вече имплементирано)
- Регулярни `ANALYZE TABLE` за MySQL
- Database indexes (провери дали са достатъчни)

**Static Files:**
- CDN за static files (Cloudflare, AWS CloudFront)
- Gzip compression в nginx

**Caching:**
- Redis за session storage
- Template caching
- Query caching

### 14. Security Headers

Всички са автоматично активирани когато `DEBUG=False`:
- HSTS
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy

### 15. Rate Limiting (Опционално)

Инсталирай `django-ratelimit`:
```bash
pip install django-ratelimit
```

Добави в `settings.py`:
```python
INSTALLED_APPS += ['django_ratelimit']
```

### 16. Testing

```bash
# Проверка преди deployment
python3 manage.py check --deploy
python3 manage.py test
```

### 17. Deployment Steps

1. ✅ Клонирай код
2. ✅ Създай virtual environment
3. ✅ Инсталирай dependencies: `pip install -r requirements.txt`
4. ✅ Копирай `.env.example` към `.env` и попълни
5. ✅ Настрой database и миграции
6. ✅ Събери static files: `python3 manage.py collectstatic`
7. ✅ Тествай локално
8. ✅ Настрой Gunicorn
9. ✅ Настрой Nginx
10. ✅ Настрой SSL
11. ✅ Настрой monitoring
12. ✅ Настрой backups
13. ✅ Тествай production

### 18. Post-Deployment

- [ ] Провери health endpoint
- [ ] Тествай регистрация
- [ ] Тествай поръчка
- [ ] Провери email изпращане
- [ ] Провери Stripe webhooks
- [ ] Мониторинг на логовете
- [ ] Настрой alerts

### 19. Maintenance

**Регулярни задачи:**
- Database backups (дневно)
- Security updates (седмично)
- Log rotation (автоматично)
- Performance monitoring (постоянно)

### 20. Troubleshooting

**Проверка на логове:**
```bash
tail -f logs/django.log
```

**Проверка на health:**
```bash
curl https://yourdomain.com/health/
```

**Проверка на database:**
```bash
python3 manage.py dbshell
```

## 🆘 Support

При проблеми:
1. Провери логовете
2. Провери health endpoint
3. Провери database connection
4. Провери email настройки
5. Провери Stripe credentials

## 📚 Допълнителна Документация

- `EMAIL_AUTOMATION.md` - Email настройки
- `TESTING_EMAILS.md` - Тестване на имейли
- `SETUP_REAL_EMAILS.md` - Production email
- `FIX_TIMEZONE.md` - MySQL timezone

