# 🚂 Phusion Passenger Deployment Guide

## 📋 Какво е Passenger?

**Phusion Passenger** е application server който се използва за:
- Ruby on Rails
- Python/Django
- Node.js
- PHP

Той се интегрира директно с **Apache** или **Nginx** и е много лесен за настройка.

---

## ✅ Текущо Състояние

Имаш `passenger_wsgi.py` файл, което означава че можеш да deploy-неш на:

### 1. **Shared Hosting с Passenger Support**
- DreamHost ⭐
- A2 Hosting
- SiteGround
- InMotion Hosting

### 2. **VPS с Passenger**
- DigitalOcean Droplet
- Vultr
- Linode
- AWS EC2

---

## 🎯 Препоръки

### За Shared Hosting (DreamHost, A2, etc.):

**✅ ДА, използвай Passenger ако:**
- Имаш shared hosting с Passenger support
- Искаш най-лесното решение
- Не искаш да управляваш сървъра

**❌ НЕ, не използвай Passenger ако:**
- Искаш Docker
- Искаш най-модерното решение
- Искаш Railway/Render/Heroku

### За VPS:

**✅ ДА, използвай Passenger ако:**
- Имаш опит с Apache/Nginx
- Искаш интеграция с вече съществуващ web server
- Искаш стабилност

**❌ НЕ, не използвай Passenger ако:**
- Искаш Docker (използвай Gunicorn + Nginx)
- Искаш най-простото решение (използвай Railway/Render)

---

## 🚀 Deployment с Passenger

### Вариант 1: DreamHost (Най-лесно)

#### Стъпка 1: Регистрация
1. Регистрирай се на [DreamHost](https://www.dreamhost.com/)
2. Избери Shared Hosting план ($2.59-4.95/месец)
3. Добави domain

#### Стъпка 2: Upload Code
```bash
# Използвай SFTP или Git
git clone https://github.com/yourusername/marbaras.git
# или upload чрез FTP client
```

#### Стъпка 3: Настрой Passenger
1. DreamHost Panel → Domains → Manage
2. Enable "Passenger" за твоя domain
3. DreamHost автоматично използва `passenger_wsgi.py`

#### Стъпка 4: Настрой Environment
1. Създай `.env` файл в root директорията
2. DreamHost автоматично зарежда environment variables

#### Стъпка 5: Database
1. DreamHost Panel → MySQL Databases
2. Създай database и user
3. Добави credentials в `.env`

#### Стъпка 6: Миграции
```bash
# SSH в DreamHost
ssh username@yourdomain.com

# Отиди в project директория
cd ~/yourdomain.com

# Миграции
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py collectstatic --noinput
```

---

### Вариант 2: VPS с Passenger + Nginx

#### Стъпка 1: Инсталирай Passenger

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y dirmngr gnupg
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 561F9B9CAC40B2F7
sudo sh -c 'echo deb https://oss-binaries.phusionpassenger.com/apt/passenger focal main > /etc/apt/sources.list.d/passenger.list'
sudo apt update
sudo apt install -y nginx passenger
```

#### Стъпка 2: Настрой Nginx

Създай `/etc/nginx/sites-available/marbaras`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/marbaras;

    passenger_enabled on;
    passenger_python /usr/bin/python3;
    passenger_app_root /var/www/marbaras;

    # Static files
    location /static/ {
        alias /var/www/marbaras/staticfiles/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /var/www/marbaras/media/;
        expires 7d;
    }
}
```

#### Стъпка 3: Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/marbaras /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Стъпка 4: SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 📝 Проверка на passenger_wsgi.py

Твоят `passenger_wsgi.py` трябва да:

1. ✅ Добавя project path в sys.path
2. ✅ Set Django settings module
3. ✅ Return WSGI application

**Примерен правилен файл:**

```python
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'МагазинСребро.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

---

## 🔄 Passenger vs Gunicorn

### Passenger:
- ✅ Интеграция с Apache/Nginx
- ✅ Автоматично process management
- ✅ Лесно за shared hosting
- ❌ По-малко популярно за Django
- ❌ По-сложно за Docker

### Gunicorn (препоръчано):
- ✅ Стандарт за Django
- ✅ Лесно за Docker
- ✅ По-гъвкаво
- ✅ По-добра документация
- ❌ Трябва да се управлява отделно

---

## 💡 Моя Препоръка

### Ако имаш Shared Hosting с Passenger:
**✅ Използвай Passenger** - най-лесното решение!

### Ако имаш VPS или искаш Docker:
**✅ Използвай Gunicorn + Nginx** - по-модерно и стандартно!

### Ако искаш най-лесното:
**✅ Използвай Railway/Render с Docker** - zero configuration!

---

## 🎯 Следващи Стъпки

1. **Ако имаш shared hosting:** Следвай DreamHost инструкциите
2. **Ако имаш VPS:** Избери между Passenger или Gunicorn
3. **Ако искаш най-лесно:** Използвай Railway/Render с Docker

---

## 📚 Допълнителни Ресурси

- [Passenger Documentation](https://www.phusionpassenger.com/docs/)
- `HOSTING_OPTIONS.md` - за hosting платформи
- `DEPLOY_DOCKER.md` - за Docker deployment
- `DEPLOY_RAILWAY.md` - за Railway (препоръчано)

---

**Моя препоръка:** Ако нямаш специфичен shared hosting, използвай **Railway/Render с Docker** - по-модерно и по-лесно! 🚀

