# 🚨 Render Database Setup - Fix "Can't connect to local server"

## Проблем

Виждаш грешка:
```
OperationalError: (2002, "Can't connect to local server through socket '/run/mysqld/mysqld.sock' (2)")
```

**Причина:** Django се опитва да се свърже с `localhost` MySQL, защото няма настроени database environment variables в Render.

---

## ✅ Решение: Настрой Database в Render

### Стъпка 1: Създай Database Service (ако нямаш)

1. В Render Dashboard → "New +" → "PostgreSQL" (препоръчително) или "MySQL"
2. Настройки:
   - **Name:** `marbaras-db`
   - **Database:** `marbaras` (или `silvershop`)
   - **Region:** Същия като web service
3. Click **"Create Database"**
4. **Изчакай** database да се създаде (няколко минути)

### Стъпка 2: Свържи Database към Web Service

1. Отиди в твоя **Web Service** (`marbarassilver`)
2. Отиди на **"Connections"** tab (в ляво меню, под "MANAGE")
3. Трябва да видиш твоя database service в списъка
4. Click **"Connect"** до database service-а
5. Render **автоматично** добавя `DATABASE_URL` environment variable!

### Стъпка 3: Провери Environment Variables

1. В Web Service → **"Environment"** tab
2. Провери дали имаш `DATABASE_URL`:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```
   Или за MySQL:
   ```
   DATABASE_URL=mysql://user:password@host:3306/dbname
   ```

**Ако НЕ виждаш `DATABASE_URL`:**
- Връщай се на Connections tab
- Убеди се че database е свързан
- Или добави ръчно в Environment Variables

### Стъпка 4: Ако използваш MySQL (ръчно настройка)

Ако използваш MySQL и Render не добавя автоматично, добави ръчно:

1. Отиди в Database Service dashboard
2. Копирай connection details:
   - Host
   - Port (3306)
   - Database name
   - Username
   - Password

3. В Web Service → Environment, добави:
   ```
   MYSQL_HOST=от-database-dashboard
   MYSQL_PORT=3306
   MYSQL_DATABASE=от-database-dashboard
   MYSQL_USER=от-database-dashboard
   MYSQL_PASSWORD=от-database-dashboard
   ```

### Стъпка 5: Redeploy

1. Click **"Save Changes"** в Environment tab
2. Отиди на **"Manual Deploy"** → **"Deploy latest commit"**
3. Провери **"Logs"** tab дали database connection е успешен

---

## 🔍 Проверка

### Провери дали работи:

1. В Logs tab, търси:
   - ✅ `✅ Database connection successful!`
   - ✅ `Running migrations...`
   - ❌ НЕ трябва да виждаш `Can't connect to local server`

2. Отвори health endpoint:
   ```
   https://marbarassilver.onrender.com/health/
   ```
   
   Трябва да видиш:
   ```json
   {
     "status": "healthy",
     "checks": {
       "database": "ok"
     }
   }
   ```

---

## 📋 Checklist

- [ ] Database service е създаден в Render
- [ ] Database service е свързан в Connections tab
- [ ] `DATABASE_URL` е в Environment Variables (или MySQL variables)
- [ ] Web service е redeployed
- [ ] Logs показват успешна database connection
- [ ] Health endpoint показва `"database": "ok"`

---

## 🚨 Ако проблемът продължава

### Провери:

1. **Database service status:**
   - Отиди в Database Service dashboard
   - Убеди се че status е **"Available"** (не "Paused")

2. **Environment Variables:**
   - Убеди се че `DATABASE_URL` или MySQL variables са правилни
   - Провери дали няма правописни грешки

3. **Connections:**
   - Убеди се че database е свързан в Connections tab
   - Ако не е, click "Connect"

4. **Logs:**
   - Провери конкретните error messages
   - Може да има проблем с credentials или network

---

## 💡 Препоръка

**Използвай PostgreSQL** вместо MySQL за Render:
- По-лесно setup
- По-добра интеграция с Render
- Автоматично добавя `DATABASE_URL`
- Безплатен план включва PostgreSQL

---

**След като направиш тези стъпки, database connection трябва да работи!** 🎉

