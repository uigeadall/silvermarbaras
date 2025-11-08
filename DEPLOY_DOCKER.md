# 🐳 Docker Deployment Guide

## 📋 Какво е Включено

- ✅ `Dockerfile` - за build на приложението
- ✅ `docker-compose.yml` - за local development
- ✅ `nginx.conf` - за reverse proxy
- ✅ `.dockerignore` - оптимизация на build

---

## 🚀 Local Development с Docker

### Стъпка 1: Инсталирай Docker

**macOS:**
```bash
# Инсталирай Docker Desktop
brew install --cask docker
```

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Стъпка 2: Подготви .env файла

Копирай `.env.example` към `.env` и попълни:
```bash
cp .env.example .env
# Редактирай .env
```

**Важно за Docker:**
```env
MYSQL_HOST=db
MYSQL_PORT=3306
REDIS_URL=redis://redis:6379/0
```

### Стъпка 3: Build и Start

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Провери logs
docker-compose logs -f web
```

### Стъпка 4: Миграции и Superuser

```bash
# Миграции
docker-compose exec web python manage.py migrate

# Създай superuser
docker-compose exec web python manage.py createsuperuser

# Събери static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Стъпка 5: Достъп

- **Web:** http://localhost:8000
- **Admin:** http://localhost:8000/admin/
- **Health:** http://localhost:8000/health/

---

## 📦 Полезни Docker Команди

```bash
# Стартирай всички services
docker-compose up -d

# Спри всички services
docker-compose down

# Рестартирай service
docker-compose restart web

# Виж logs
docker-compose logs -f web
docker-compose logs -f db

# Влез в container
docker-compose exec web bash
docker-compose exec db mysql -u root -p

# Rebuild след промени
docker-compose up -d --build

# Изтрий всичко (включително volumes)
docker-compose down -v
```

---

## 🌐 Production Deployment с Docker

### Вариант 1: Railway (Препоръчано)

1. Регистрирай се на [Railway](https://railway.app/)
2. New Project → Deploy from GitHub
3. Connect GitHub repo
4. Add Database → MySQL
5. Add Redis (опционално)
6. Railway автоматично детектира Dockerfile
7. Добави environment variables в Railway dashboard
8. Deploy!

**Цена:** $5-20/месец

---

### Вариант 2: Render

1. Регистрирай се на [Render](https://render.com/)
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - **Build Command:** `docker build -t marbaras .`
   - **Start Command:** `docker run -p 10000:8000 marbaras`
5. Add MySQL database
6. Add Redis (опционално)
7. Добави environment variables
8. Deploy!

**Цена:** $7-25/месец

---

### Вариант 3: DigitalOcean App Platform

1. Регистрирай се на [DigitalOcean](https://www.digitalocean.com/)
2. Create → App Platform
3. Connect GitHub repo
4. DigitalOcean автоматично детектира Dockerfile
5. Add Database → MySQL
6. Add Redis (опционално)
7. Добави environment variables
8. Deploy!

**Цена:** $12-25/месец

---

### Вариант 4: VPS (DigitalOcean Droplet, Vultr, etc.)

#### Стъпка 1: Създай VPS

1. Създай Droplet/VPS (Ubuntu 22.04)
2. SSH в сървъра:
```bash
ssh root@your-server-ip
```

#### Стъпка 2: Инсталирай Docker

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y
```

#### Стъпка 3: Deploy Code

```bash
# Клонирай repo
git clone https://github.com/yourusername/marbaras.git
cd marbaras

# Копирай .env
cp .env.example .env
nano .env  # Редактирай

# Build и start
docker-compose -f docker-compose.prod.yml up -d --build
```

#### Стъпка 4: Настрой SSL (Let's Encrypt)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot certonly --standalone -d yourdomain.com

# Update nginx.conf с SSL paths
# Restart nginx
docker-compose restart nginx
```

---

## 🔧 Production Docker Compose

Създай `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 МагазинСребро.wsgi:application
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env
    depends_on:
      - db
    restart: always

  db:
    image: mysql:8.0
    volumes:
      - db_data:/var/lib/mysql
    environment:
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${MYSQL_PASSWORD}
    restart: always
    command: --default-authentication-plugin=mysql_native_password

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    restart: always

volumes:
  db_data:
  static_volume:
  media_volume:
```

---

## ✅ Checklist за Docker Deployment

- [ ] Docker инсталиран
- [ ] `.env` файл конфигуриран
- [ ] `docker-compose build` успешен
- [ ] Миграции приложени
- [ ] Superuser създаден
- [ ] Static files събрани
- [ ] Health endpoint работи
- [ ] SSL сертификат (за production)
- [ ] Backups настройки
- [ ] Monitoring настройки

---

## 🆘 Troubleshooting

### Проблем: Database connection failed

**Решение:**
```bash
# Провери дали db service работи
docker-compose ps

# Провери logs
docker-compose logs db

# В .env използвай:
MYSQL_HOST=db  # не localhost!
```

### Проблем: Static files не се показват

**Решение:**
```bash
# Събери static files
docker-compose exec web python manage.py collectstatic --noinput

# Провери nginx volume mapping
docker-compose exec nginx ls -la /app/staticfiles
```

### Проблем: Port already in use

**Решение:**
```bash
# Промени портовете в docker-compose.yml
ports:
  - "8001:8000"  # вместо 8000:8000
```

---

## 📚 Допълнителни Ресурси

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- `HOSTING_OPTIONS.md` - за hosting платформи

---

**Следваща стъпка:** Избери hosting платформа и следвай инструкциите! 🚀

