# 🔌 Свързване със Съществуваща База Данни

## Поддържани Методи

Проектът поддържа **3 начина** за свързване с база данни:

### 1. DATABASE_URL (Препоръчано за Render/Railway/Heroku)

```env
# Формат: mysql://user:password@host:port/database
DATABASE_URL=mysql://marbaras:password123@db.example.com:3306/silvershop

# Или за PostgreSQL:
DATABASE_URL=postgresql://user:password@host:5432/database
```

**Предимства:**
- Автоматично парсване на connection string
- Поддръжка на MySQL и PostgreSQL
- Работи с Render, Railway, Heroku и други платформи

### 2. Индивидуални Environment Variables (За съществуваща база)

```env
MYSQL_DATABASE=silvershop
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_HOST=your-database-host.com
MYSQL_PORT=3306
```

**Предимства:**
- Пълна контрол над настройките
- Лесно за локална база данни
- Работи с всяка MySQL/MariaDB база

### 3. Локална База (Development)

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=silvershop
MYSQL_USER=root
MYSQL_PASSWORD=your_local_password
```

---

## 🔧 Настройки за Production

### Connection Pooling

```env
# Включи connection pooling за по-добра производителност
DB_CONN_MAX_AGE=600  # 10 минути (секунди)
```

### Timeout Settings

```env
# Database connection timeout (секунди)
# По подразбиране: 10 секунди
```

---

## 📋 Стъпки за Свързване

### Стъпка 1: Подготви Database Credentials

Убеди се че имаш:
- ✅ Database host (IP или домейн)
- ✅ Database port (3306 за MySQL, 5432 за PostgreSQL)
- ✅ Database name
- ✅ Username
- ✅ Password

### Стъпка 2: Настрой Environment Variables

**За Render/Railway:**
- Добави `DATABASE_URL` в Environment Variables
- Или свържи Database service (автоматично добавя променливите)

**За VPS/Docker:**
- Добави променливите в `.env` файл
- Или използвай `DATABASE_URL`

### Стъпка 3: Тествай Connection

```bash
# Провери connection
python manage.py dbshell

# Или провери health endpoint
curl http://localhost:8000/health/
```

### Стъпка 4: Приложи Миграции

```bash
# Миграции се изпълняват автоматично при стартиране (entrypoint.sh)
# Или ръчно:
python manage.py migrate
```

---

## 🚨 Troubleshooting

### Проблем: Cannot connect to database

**Решения:**
1. Провери дали database host е достъпен
2. Провери firewall настройки
3. Провери credentials
4. Провери дали database server приема connections от твоя IP

### Проблем: Access denied

**Решения:**
1. Провери username и password
2. Провери дали user има права за достъп до database
3. Провери дали user може да се свърже от твоя host

### Проблем: Connection timeout

**Решения:**
1. Увеличи timeout в settings.py
2. Провери мрежовата свързаност
3. Провери дали database server работи

---

## 📊 Database Monitoring

### Health Check

Health endpoint автоматично проверява database connection:
```
GET /health/
```

Отговор:
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok"
  }
}
```

### Логове

Database errors се записват в:
- Console logs (development)
- `logs/django.log` (production)

---

## 🔐 Security Best Practices

1. **Никога не комитирай credentials в git**
2. **Използвай силни пароли**
3. **Ограничи достъпа до database по IP**
4. **Използвай SSL/TLS за database connections** (ако е възможно)
5. **Регулярно backup-вай базата данни**

---

## 📚 Допълнителна Документация

- `PRODUCTION_README.md` - Пълно production ръководство
- `DEPLOY_RENDER.md` - Render deployment с database
- `DEPLOY_DOCKER.md` - Docker deployment

---

**Готово!** Сега можеш да се свържеш с всяка съществуваща база данни! 🎉

