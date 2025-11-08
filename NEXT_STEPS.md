# 🎯 Следващи Стъпки - Production Deployment

## ✅ Какво е готово

- ✅ Production-ready код
- ✅ Security настройки
- ✅ Error handling (404, 500)
- ✅ Health check endpoint
- ✅ Logging система
- ✅ Database backup script
- ✅ Email automation
- ✅ Документация

## 🚀 Следващи Стъпки (По Приоритет)

### 1. **НЕЗАБАВНО: Подготовка за Deployment**

#### Стъпка 1.1: Настрой Environment Variables
```bash
# Копирай template
cp .env.example .env

# Редактирай .env и попълни:
# - DJANGO_SECRET_KEY (генерирай нов!)
# - DJANGO_DEBUG=False (за production)
# - DJANGO_ALLOWED_HOSTS (твоите домейни)
# - MYSQL_PASSWORD (силна парола)
# - STRIPE_SECRET_KEY (production ключ)
# - EMAIL_* (production SMTP)
```

**Генерирай SECRET_KEY:**
```python
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Стъпка 1.2: Тествай Health Endpoint
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
    "cache": "not_configured",
    "stripe": "configured"
  }
}
```

#### Стъпка 1.3: Проверка преди Deployment
```bash
# Провери всичко
python3 manage.py check --deploy

# Събери static files
python3 manage.py collectstatic --noinput

# Провери миграции
python3 manage.py showmigrations
python3 manage.py migrate
```

### 2. **ВАЖНО: Production Настройки**

#### Стъпка 2.1: Настрой Production Email
Виж `SETUP_REAL_EMAILS.md`:
- Gmail (най-лесно)
- SendGrid (препоръчано)
- Mailgun (алтернатива)

#### Стъпка 2.2: Настрой Stripe Production
- Смени на production API keys в `.env`
- Настрой webhook endpoint в Stripe Dashboard
- Тествай с малка сума

#### Стъпка 2.3: Database Timezone (ако не е направено)
```bash
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql
```

### 3. **DEPLOYMENT: Server Setup**

#### Стъпка 3.1: Избери Hosting
**Опции:**
- **DigitalOcean** - лесно, добра документация
- **AWS** - по-сложно, но мощно
- **Heroku** - най-лесно, но по-скъпо
- **VPS** (Linode, Vultr) - контрол, добра цена

#### Стъпка 3.2: Server Setup (Ubuntu/Debian)
```bash
# Обновяване
sudo apt update && sudo apt upgrade -y

# Инсталирай Python, MySQL, Nginx
sudo apt install python3-pip python3-venv mysql-server nginx -y

# Инсталирай Gunicorn
pip3 install gunicorn
```

#### Стъпка 3.3: Deploy Code
```bash
# Клонирай проект
git clone <your-repo> /var/www/marbaras
cd /var/www/marbaras

# Създай virtual environment
python3 -m venv venv
source venv/bin/activate

# Инсталирай dependencies
pip install -r requirements.txt

# Настрой .env файл
cp .env.example .env
nano .env  # Редактирай с production стойности
```

#### Стъпка 3.4: Database Setup
```bash
# Създай database
mysql -u root -p
CREATE DATABASE silvershop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'marbaras'@'localhost' IDENTIFIED BY 'strong-password';
GRANT ALL PRIVILEGES ON silvershop.* TO 'marbaras'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Миграции
python3 manage.py migrate
python3 manage.py createsuperuser
```

#### Стъпка 3.5: Static Files
```bash
python3 manage.py collectstatic --noinput
```

#### Стъпка 3.6: Gunicorn Setup
Създай `/etc/systemd/system/marbaras.service`:
```ini
[Unit]
Description=Marbaras Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/marbaras
Environment="PATH=/var/www/marbaras/venv/bin"
ExecStart=/var/www/marbaras/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/run/gunicorn.sock \
    МагазинСребро.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start marbaras
sudo systemctl enable marbaras
```

#### Стъпка 3.7: Nginx Setup
Създай `/etc/nginx/sites-available/marbaras`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }

    location /static/ {
        alias /var/www/marbaras/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/marbaras/media/;
        expires 7d;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/marbaras /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Стъпка 3.8: SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 4. **POST-DEPLOYMENT: Тестване**

#### Стъпка 4.1: Smoke Tests
```bash
# Health check
curl https://yourdomain.com/health/

# Провери главна страница
curl https://yourdomain.com/

# Провери admin
# Отиди на https://yourdomain.com/admin/
```

#### Стъпка 4.2: Функционални Тестове
- [ ] Регистрация на нов потребител
- [ ] Login/Logout
- [ ] Преглед на продукти
- [ ] Добавяне в кошница
- [ ] Checkout процес
- [ ] Тестова поръчка (малка сума)
- [ ] Email изпращане
- [ ] Admin панел

#### Стъпка 4.3: Monitoring Setup
- Настрой UptimeRobot/Pingdom за `/health/`
- Провери логове: `tail -f /var/www/marbaras/logs/django.log`
- Настрой alerts за errors

### 5. **ОПЦИОНАЛНО: Подобрения**

#### 5.1: Caching (Redis)
```bash
sudo apt install redis-server
# В .env добави: REDIS_URL=redis://localhost:6379/0
# В settings.py добави CACHES конфигурация (виж PRODUCTION_README.md)
```

#### 5.2: Error Tracking (Sentry)
```bash
pip install sentry-sdk
# Настрой в settings.py
```

#### 5.3: Rate Limiting
```bash
pip install django-ratelimit
# Добави в INSTALLED_APPS и използвай декоратори
```

#### 5.4: CDN за Static Files
- Cloudflare (безплатно)
- AWS CloudFront
- Настрой в nginx

### 6. **MAINTENANCE: Регулярни Задачи**

#### Автоматични Backups
```bash
# Добави в crontab
crontab -e

# Дневен backup в 2:00 сутринта
0 2 * * * /var/www/marbaras/scripts/backup_db.sh
```

#### Регулярни Updates
```bash
# Седмично проверявай за updates
pip list --outdated
sudo apt update && sudo apt upgrade
```

## 📋 Quick Reference

### Важни Команди
```bash
# Проверка
python3 manage.py check --deploy

# Health check
curl http://localhost:8000/health/

# Static files
python3 manage.py collectstatic --noinput

# Миграции
python3 manage.py migrate

# Backup
./scripts/backup_db.sh

# Логове
tail -f logs/django.log

# Restart services
sudo systemctl restart marbaras
sudo systemctl restart nginx
```

### Важни Файлове
- `.env` - Environment variables (НЕ комитирай!)
- `.env.example` - Template
- `PRODUCTION_README.md` - Пълно ръководство
- `PRODUCTION_CHECKLIST.md` - Checklist
- `scripts/backup_db.sh` - Backup script

## 🆘 При Проблеми

1. **Провери логове:** `tail -f logs/django.log`
2. **Провери health:** `curl https://yourdomain.com/health/`
3. **Провери database:** `python3 manage.py dbshell`
4. **Провери nginx:** `sudo nginx -t`
5. **Провери gunicorn:** `sudo systemctl status marbaras`

## ✅ Готовност за Production

Проектът е **production-ready** когато:
- [x] Всички security настройки са активни
- [x] DEBUG=False
- [x] Production SECRET_KEY
- [x] SSL сертификат
- [x] Database backups
- [x] Monitoring настройки
- [x] Email работи
- [x] Stripe работи
- [x] Health check работи

---

**Следваща стъпка:** Настрой `.env` файла и тествай health endpoint! 🚀

