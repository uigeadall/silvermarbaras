# 🗄️ Използване на MySQL в Railway

## План

1. ✅ Експортирай данните от локалната MySQL база
2. ✅ Използвай MySQL service в Railway (вече имаш такъв!)
3. ✅ Импортирай данните в Railway MySQL
4. ✅ Настрой `DATABASE_URL` да сочи към MySQL

---

## Стъпка 1: Експортирай данните от локалната MySQL база

### Опция A: Използвай Django dumpdata (Препоръчително)

```bash
# Убеди се че .env файлът сочи към локалната MySQL база
python3 manage.py dumpdata > data.json
```

Това ще експортира всички данни в JSON формат, който Django може лесно да импортира.

### Опция B: Използвай mysqldump (SQL формат)

```bash
# Експортирай цялата база
mysqldump -u root -p silvershop > backup.sql

# Или само данните (без структура)
mysqldump -u root -p --no-create-info silvershop > data_only.sql
```

**Забележка:** Ако използваш `mysqldump`, ще трябва да импортираш SQL файла в Railway MySQL.

---

## Стъпка 2: Провери MySQL Service в Railway

1. В Railway Dashboard → Architecture view
2. Убеди се че имаш **MySQL** service (вече го виждаш!)
3. Ако нямаш:
   - "+ Create" → "Database" → "MySQL"
   - Създай MySQL service

---

## Стъпка 3: Свържи MySQL към Web Service

1. В Railway Dashboard → Architecture view
2. Click на **MySQL** service
3. Отиди на **"Settings"** tab
4. Търси **"Connect"** или **"Add to Project"** бутон
5. Click и избери **`marbaras`** web service
6. Railway автоматично добавя `DATABASE_URL` environment variable!

**Важно:** Railway ще добави `DATABASE_URL` във формат:
```
mysql://user:password@host:3306/database
```

---

## Стъпка 4: Провери DATABASE_URL в Railway

1. Click на **`marbaras`** web service
2. Отиди на **"Variables"** tab
3. Провери дали имаш `DATABASE_URL`:
   ```
   DATABASE_URL=mysql://user:password@host:3306/database
   ```
4. Ако **НЕ** го виждаш:
   - MySQL не е свързан към web service
   - Върни се на Стъпка 3

---

## Стъпка 5: Премахни PostgreSQL (ако не го използваш)

Ако не използваш PostgreSQL (`marbaras-db`):

1. Click на **`marbaras-db`** (PostgreSQL) service
2. Отиди на **"Settings"** tab
3. Scroll down до **"Danger Zone"**
4. Click **"Delete Service"**
5. Това ще премахне объркването

---

## Стъпка 6: Импортирай данните в Railway MySQL

### Опция A: Използвай Django loaddata (Ако използваш dumpdata)

1. В Railway Dashboard → `marbaras` web service → **"Deployments"** tab
2. Click на последния deployment → **"View Logs"**
3. Или използвай Railway Shell:
   - `marbaras` service → **"Shell"** tab
   - В shell терминала:
   ```bash
   python manage.py migrate
   python manage.py loaddata data.json
   ```

**Проблем:** Как да качиш `data.json` в Railway?

**Решение 1: Използвай Railway CLI**
```bash
# Инсталирай Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link към проекта
railway link

# Качи файла
railway run python manage.py loaddata data.json
```

**Решение 2: Използвай Railway Shell и копирай съдържанието**
1. Отвори Railway Shell
2. Създай файл:
   ```bash
   nano data.json
   ```
3. Постави съдържанието от локалния `data.json`
4. Save (Ctrl+O, Enter, Ctrl+X)
5. Импортирай:
   ```bash
   python manage.py loaddata data.json
   ```

### Опция B: Използвай mysqldump (Ако използваш SQL файл)

1. Вземи MySQL connection details от Railway:
   - MySQL service → **"Variables"** tab
   - Копирай: `MYSQLHOST`, `MYSQLPORT`, `MYSQLDATABASE`, `MYSQLUSER`, `MYSQLPASSWORD`

2. Локално, импортирай:
   ```bash
   mysql -h MYSQLHOST -P MYSQLPORT -u MYSQLUSER -p MYSQLDATABASE < backup.sql
   ```

---

## Стъпка 7: Провери че всичко работи

1. В Railway Dashboard → `marbaras` web service → **"Logs"** tab
2. Провери дали има грешки
3. Отвори приложението в браузъра
4. Провери дали продуктите са там!

---

## Важно: DATABASE_URL формат за MySQL

В Railway, `DATABASE_URL` трябва да изглежда така:

```
mysql://user:password@host:3306/database
```

**НЕ** `postgresql://` - това е за PostgreSQL!

---

## Troubleshooting

### Проблем: Django все още се опитва да се свърже с PostgreSQL

**Решение:**
1. Провери дали `DATABASE_URL` започва с `mysql://` (НЕ `postgresql://`)
2. Премахни всички `POSTGRES_*` environment variables
3. Премахни PostgreSQL service (ако не го използваш)
4. Redeploy web service

### Проблем: Foreign key constraints при loaddata

**Решение:**
```bash
python manage.py loaddata data.json --natural-foreign --natural-primary
```

### Проблем: Encoding issues

**Решение:**
```bash
# Експортирай с правилно encoding
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 > data.json
```

---

## Резюме

1. ✅ Експортирай данните: `python3 manage.py dumpdata > data.json`
2. ✅ Свържи MySQL service към `marbaras` web service в Railway
3. ✅ Провери че `DATABASE_URL` е добавен (трябва да започва с `mysql://`)
4. ✅ Импортирай данните: `python manage.py loaddata data.json`
5. ✅ Премахни PostgreSQL service (ако не го използваш)
6. ✅ Готово! 🎉

---

## Следващи стъпки

След като всичко работи:
- [ ] Тествай приложението
- [ ] Провери дали продуктите са там
- [ ] Настрой други environment variables (Stripe, Email, etc.)

