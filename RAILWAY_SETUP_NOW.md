# 🚨 Railway Setup - КРИТИЧНО: Настрой DATABASE_URL

## Проблем

Виждаш грешки за MySQL connection, защото `DATABASE_URL` не е настроен в Railway.

---

## ✅ РЕШЕНИЕ: Настрой DATABASE_URL в Railway

### Стъпка 1: Отиди в Railway Dashboard

1. Отвори [railway.app](https://railway.app/)
2. Отиди в твоя проект

### Стъпка 2: Провери Database Service

1. В проекта, трябва да видиш **PostgreSQL Database** service
2. Ако НЕ го виждаш:
   - Click **"New"** → **"Database"** → **"PostgreSQL"**
   - Създай database
   - Изчакай да се създаде

### Стъпка 3: Свържи Database към Web Service

**Метод 1: От Database Service (Препоръчително)**

1. Click на **PostgreSQL Database** service
2. Отиди на **"Settings"** tab
3. Търси секция **"Connect"** или **"Add to Project"**
4. Click **"Connect"** или **"Add"**
5. Избери твоя **Web Service**
6. Railway автоматично добавя `DATABASE_URL`!

**Метод 2: От Web Service**

1. Click на **Web Service**
2. Отиди на **"Variables"** tab
3. Провери дали имаш `DATABASE_URL`
4. Ако НЕ го виждаш, database не е свързан

### Стъпка 4: Провери DATABASE_URL

В Web Service → Variables, трябва да видиш:

```
DATABASE_URL=postgresql://postgres:password@hostname:5432/railway
```

**Важно:**
- Трябва да започва с `postgresql://` или `postgres://`
- НЕ трябва да започва с `mysql://`
- Railway автоматично го добавя когато свържеш database

### Стъпка 5: Ако DATABASE_URL липсва - Добави ръчно

1. Отиди в **PostgreSQL Database** service
2. Отиди на **"Variables"** или **"Settings"** tab
3. Там ще видиш connection details:
   - `PGHOST` или `POSTGRES_HOST`
   - `PGPORT` или `POSTGRES_PORT` (5432)
   - `PGDATABASE` или `POSTGRES_DATABASE`
   - `PGUSER` или `POSTGRES_USER`
   - `PGPASSWORD` или `POSTGRES_PASSWORD`

4. В **Web Service** → **Variables**, добави:
   ```
   DATABASE_URL=postgresql://PGUSER:PGPASSWORD@PGHOST:5432/PGDATABASE
   ```
   
   Замени `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGDATABASE` с реалните стойности!

### Стъпка 6: Redeploy

1. Save Variables
2. Railway автоматично ще redeploy-не
3. Провери logs дали database connection е успешен

---

## 🔍 Как да провериш в Railway

### Проверка 1: Database Variables

1. PostgreSQL Database → "Variables" tab
2. Там ще видиш всички connection details
3. Копирай ги

### Проверка 2: Web Service Variables

1. Web Service → "Variables" tab
2. Търси `DATABASE_URL`
3. Трябва да видиш нещо като:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/db
   ```

### Проверка 3: Connections

1. В проекта dashboard
2. Провери дали има линия между Database и Web Service
3. Ако няма, database не е свързан

---

## 📋 Бърз Checklist

- [ ] PostgreSQL Database service съществува
- [ ] Database е свързан към Web Service
- [ ] `DATABASE_URL` е в Web Service Variables
- [ ] `DATABASE_URL` започва с `postgresql://`
- [ ] Web Service е redeployed
- [ ] Logs показват успешна database connection

---

## 🚨 Ако все още не работи

### Debug Steps:

1. **Провери Database Variables:**
   - Отиди в PostgreSQL Database → Variables
   - Копирай всички `PG*` или `POSTGRES_*` variables
   - Използвай ги за да създадеш `DATABASE_URL`

2. **Провери Web Service Variables:**
   - Убеди се че няма `MYSQL_*` variables които override-ват `DATABASE_URL`
   - Премахни всички `MYSQL_*` variables ако използваш PostgreSQL

3. **Провери Logs:**
   - Web Service → View Logs
   - Търси за конкретни database errors
   - Сподели ги тук

---

**НАЙ-ВАЖНО:** Убеди се че `DATABASE_URL` е настроен в Railway Variables и започва с `postgresql://`! 🎯

