# 🔧 Railway Database Connection Fix

## Проблем

Виждаш грешка:
```
OperationalError: (2002, "Can't connect to local server through socket '/run/mysqld/mysqld.sock' (2)")
```

**Причина:** Django се опитва да се свърже с MySQL вместо PostgreSQL, защото `DATABASE_URL` не е настроен в Railway.

---

## ✅ Решение: Настрой DATABASE_URL в Railway

### Стъпка 1: Провери дали Database е свързан

1. В Railway Dashboard → твоя проект
2. Убеди се че виждаш **2 services**:
   - Web Service (Django app)
   - PostgreSQL Database
3. Ако НЕ виждаш database service:
   - "New" → "Database" → "PostgreSQL"
   - Създай database

### Стъпка 2: Свържи Database към Web Service

**Важно:** Railway автоматично добавя `DATABASE_URL` когато свържеш database!

1. В Railway Dashboard → твоя проект
2. Click на **PostgreSQL Database** service
3. Отиди на **"Settings"** tab
4. В секцията **"Connections"** или **"Variables"**
5. Трябва да видиш **"Connect"** бутон или **"Add to Project"**
6. Click и избери твоя Web Service
7. Railway автоматично добавя `DATABASE_URL` environment variable!

**Алтернативно:**
1. Click на **Web Service**
2. Отиди на **"Variables"** tab
3. Трябва да видиш `DATABASE_URL` автоматично добавен
4. Ако НЕ го виждаш, database не е свързан

### Стъпка 3: Провери DATABASE_URL Format

В Railway Variables, `DATABASE_URL` трябва да изглежда така:

```
postgresql://postgres:password@hostname:5432/railway
```

Или:
```
postgres://user:password@host:5432/dbname
```

**Важно:** Трябва да започва с `postgresql://` или `postgres://`, НЕ `mysql://`!

### Стъпка 4: Ако DATABASE_URL липсва

Ако Railway не добавя автоматично `DATABASE_URL`:

1. Отиди в **PostgreSQL Database** service
2. Отиди на **"Settings"** или **"Variables"** tab
3. Там ще видиш connection details:
   - Host
   - Port (5432)
   - Database name
   - Username
   - Password
4. Създай `DATABASE_URL` ръчно в Web Service Variables:
   ```
   DATABASE_URL=postgresql://username:password@host:5432/database_name
   ```

### Стъпка 5: Redeploy

1. Save Variables
2. Railway автоматично ще redeploy-не
3. Провери logs дали database connection е успешен

---

## 🔍 Как да провериш в Railway

### Проверка 1: Database Service

1. В проекта → Click на PostgreSQL Database
2. Провери status - трябва да е **"Running"**
3. Отиди на **"Variables"** tab
4. Там ще видиш connection details

### Проверка 2: Web Service Variables

1. Click на Web Service
2. Отиди на **"Variables"** tab
3. Търси за `DATABASE_URL`
4. Трябва да видиш нещо като:
   ```
   DATABASE_URL=postgresql://...
   ```

### Проверка 3: Connections

1. В проекта dashboard
2. Провери дали database service е свързан към web service
3. Обикновено се вижда като линия между двата services

---

## 🚨 Ако проблемът продължава

### Опция 1: Добави DATABASE_URL ръчно

1. В PostgreSQL Database → "Variables" или "Settings"
2. Копирай connection details
3. В Web Service → "Variables"
4. Добави:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

### Опция 2: Провери Railway Documentation

Railway има специфичен начин за свързване на databases. Провери:
- Railway Dashboard → Database → "Connect" или "Add to Project"

---

## ✅ След Fix

След като настроиш `DATABASE_URL`, в logs трябва да видиш:

```
✅ Database connection successful!
Running migrations...
```

И НЕ трябва да виждаш:
- `Can't connect to local server`
- `mysql_is_mariadb` errors

---

**Най-важното:** Убеди се че `DATABASE_URL` е в Web Service Variables и започва с `postgresql://`! 🎯

