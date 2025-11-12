# 🔍 Как да Провериш Database Connection

## Метод 1: Проверка в Render Dashboard

### Стъпка 1: Провери Connections Tab

1. Отиди в **Render Dashboard**: https://dashboard.render.com
2. Click на твоя **Web Service**
3. Отиди на **"Connections"** tab (в ляво меню)
4. Трябва да видиш:
   - ✅ **Database service** в списъка
   - ✅ Status: **"Connected"** (зелено)
   - ✅ Име на database service-а

**Ако НЕ виждаш database:**
- Click **"Connect"** бутон
- Избери твоя database service
- Render автоматично добавя `DATABASE_URL` environment variable

### Стъпка 2: Провери Environment Variables

1. В същия Web Service, отиди на **"Environment"** tab
2. Провери дали имаш:

**За Render PostgreSQL:**
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

**За MySQL:**
```
MYSQL_HOST=...
MYSQL_DATABASE=...
MYSQL_USER=...
MYSQL_PASSWORD=...
```

---

## Метод 2: Проверка чрез Logs

### Стъпка 1: Виж Deployment Logs

1. В Render Dashboard → Web Service
2. Отиди на **"Logs"** tab
3. Търси за:
   - ✅ `✅ Database connection successful!`
   - ❌ `Database is unavailable`
   - ❌ `Connection refused`
   - ❌ `Access denied`

### Стъпка 2: Провери Runtime Logs

След като приложението е стартирало, провери logs за:
- Database connection errors
- Migration errors
- Health check status

---

## Метод 3: Проверка чрез Health Endpoint

### Стъпка 1: Отвори Health Endpoint

След като приложението е deployed, отвори:
```
https://your-app.onrender.com/health/
```

### Стъпка 2: Провери Response

Трябва да видиш:
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok"  // ✅ Това означава че database е свързан!
  }
}
```

**Ако виждаш:**
```json
{
  "status": "unhealthy",
  "checks": {
    "database": "error: ..."  // ❌ Database не е свързан
  }
}
```

---

## Метод 4: Проверка чрез Render Shell (Advanced)

### Стъпка 1: Отвори Shell

1. В Render Dashboard → Web Service
2. Click **"Shell"** tab
3. Това отваря терминал в твоя container

### Стъпка 2: Тествай Connection

```bash
# Провери database connection
python manage.py dbshell

# Ако работи, ще видиш MySQL/PostgreSQL prompt
# Напиши: exit за да излезеш
```

Или:
```bash
# Провери чрез Python
python manage.py shell
```

След това в Python shell:
```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 1")
print("✅ Database connected!")
```

---

## Метод 5: Проверка на Database Service Status

### Стъпка 1: Провери Database Service

1. В Render Dashboard, отиди на **"Databases"** (от ляво меню)
2. Click на твоя database service
3. Провери:
   - ✅ Status: **"Available"** (не "Paused")
   - ✅ Connection info е видимо
   - ✅ Internal Database URL е показан

### Стъпка 2: Провери Connection Info

В Database Service dashboard, виж:
- **Internal Database URL** - използвай това за `DATABASE_URL`
- **External Connection** - за локално тестване
- **Connection Pooling** - дали е enabled

---

## 🚨 Често Срещани Проблеми

### Проблем 1: Database не е свързан в Connections

**Решение:**
1. Отиди на Web Service → Connections
2. Click "Connect" до database service
3. Redeploy web service

### Проблем 2: DATABASE_URL липсва

**Решение:**
1. Отиди на Database Service
2. Копирай **Internal Database URL**
3. Добави го в Web Service → Environment като `DATABASE_URL`
4. Redeploy

### Проблем 3: Database е Paused

**Решение:**
1. Отиди на Database Service
2. Click **"Resume"** бутон
3. Изчакай database да се стартира
4. Redeploy web service

### Проблем 4: Access Denied

**Решение:**
1. Провери database credentials
2. Убеди се че username и password са правилни
3. Провери дали database user има права

---

## ✅ Quick Checklist

- [ ] Database service е свързан в Connections tab
- [ ] `DATABASE_URL` или MySQL variables са в Environment
- [ ] Database service status е "Available"
- [ ] Health endpoint показва `"database": "ok"`
- [ ] Няма database errors в logs

---

## 📞 Следващи Стъпки

Ако всичко е наред:
1. ✅ Database е свързан
2. ✅ Health endpoint показва "ok"
3. ✅ Няма errors в logs

Ако има проблем:
1. Провери конкретния error в logs
2. Провери database credentials
3. Убеди се че database service е Available
4. Провери Connections tab

---

**Готово!** Сега знаеш как да провериш database connection! 🎉

