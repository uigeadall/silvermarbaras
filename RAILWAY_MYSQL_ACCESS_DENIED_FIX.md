# 🔧 Railway MySQL Access Denied Fix

## Проблем

Виждаш грешка:
```
django.db.utils.OperationalError: (1045, "Access denied for user 'railway'@'...' (using password: YES)")
```

**Причина:** `DATABASE_URL` има неправилни credentials или MySQL не приема connections от този user.

---

## Решение 1: Провери MySQL Credentials

### Стъпка 1: Вземи правилните credentials от MySQL

1. В Railway Dashboard → `MySQL` service
2. Отиди на **"Database"** tab
3. Там трябва да видиш:
   - **Host**
   - **Port** (3306)
   - **Database** name
   - **Username**
   - **Password**

### Стъпка 2: Провери Variables на MySQL

1. В Railway Dashboard → `MySQL` service
2. Отиди на **"Variables"** tab
3. Търси:
   - `MYSQLUSER` или `MYSQL_USER`
   - `MYSQLPASSWORD` или `MYSQL_PASSWORD`
   - `MYSQLDATABASE` или `MYSQL_DATABASE`
   - `MYSQLHOST` или `MYSQL_HOST`

---

## Решение 2: Обнови DATABASE_URL в marbaras

### Стъпка 1: Редактирай DATABASE_URL

1. В Railway Dashboard → `marbaras` service → Variables tab
2. Кликни на `DATABASE_URL` (редактирай я)
3. Изтри текущата стойност

### Стъпка 2: Добави правилния DATABASE_URL

**Опция A: Използвай Variable Reference (Препоръчително)**

1. Кликни "Add Reference" (до "VALUE or ${{REF}}")
2. Избери `MySQL` service
3. Railway автоматично добавя правилния `DATABASE_URL`

**Опция B: Добави ръчно**

1. Вземи credentials от MySQL Variables или Database tab
2. Създай `DATABASE_URL` във формат:
   ```
   mysql://MYSQLUSER:MYSQLPASSWORD@MYSQLHOST:3306/MYSQLDATABASE
   ```
3. Замени с реалните стойности

---

## Решение 3: Провери MySQL User Permissions

### Стъпка 1: Провери дали user съществува

1. В Railway Dashboard → `MySQL` service → Database tab
2. Провери дали user `railway` съществува
3. Ако не съществува → създай нов user или използвай друг

### Стъпка 2: Провери дали user има права

MySQL user трябва да има права за:
- SELECT
- INSERT
- UPDATE
- DELETE
- CREATE
- DROP
- ALTER

---

## Решение 4: Използвай Root User (Временно)

Ако проблемът продължава, можеш временно да използваш root user:

1. В Railway Dashboard → `MySQL` service → Variables tab
2. Вземи `MYSQL_ROOT_PASSWORD`
3. Обнови `DATABASE_URL` в `marbaras`:
   ```
   mysql://root:MYSQL_ROOT_PASSWORD@mysql.railway.internal:3306/railway
   ```

**Важно:** Това е временно решение. По-добре е да използваш dedicated user.

---

## Стъпка по Стъпка Fix

### Стъпка 1: Вземи правилните credentials

1. Кликни на `MySQL` service → Database tab
2. Копирай: Host, Port, Database, Username, Password

### Стъпка 2: Обнови DATABASE_URL

1. Кликни на `marbaras` service → Variables tab
2. Редактирай `DATABASE_URL`
3. Използвай Variable Reference към MySQL (най-лесно)
4. Или добави ръчно с правилните credentials

### Стъпка 3: Deploy промените

1. В Architecture view, кликни "Deploy"
2. Изчакай deploy-а да завърши
3. Провери Deploy Logs - трябва да видиш "✅ Database connection successful!"

---

## Какво да направиш сега

1. ⚠️ Кликни на `MySQL` service → Database tab
2. ⚠️ Вземи правилните credentials (Host, Port, Database, Username, Password)
3. ⚠️ Кликни на `marbaras` service → Variables tab
4. ⚠️ Редактирай `DATABASE_URL` и използвай Variable Reference към MySQL
5. ⚠️ Deploy промените

---

## Резюме

1. Вземи правилните credentials от MySQL Database tab
2. Обнови `DATABASE_URL` в `marbaras` Variables (използвай Variable Reference)
3. Deploy промените
4. Провери Deploy Logs за "✅ Database connection successful!"

---

**Сподели какво виждаш в MySQL Database tab - какви са credentials там?**

