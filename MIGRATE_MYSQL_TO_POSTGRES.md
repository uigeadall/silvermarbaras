# 🔄 Миграция от MySQL към PostgreSQL

## Вариант 1: Използвай Django (Най-лесно)

Django поддържа и MySQL и PostgreSQL, така че можеш да прехвърлиш данните лесно!

### Стъпка 1: Създай PostgreSQL Database в Render

1. В Render Dashboard → "+ New" → "Postgres"
2. Настройки:
   - Name: `marbaras-db`
   - Database: `marbaras`
   - Region: Същия като web service
3. Click "Create Database"
4. Изчакай да се създаде

### Стъпка 2: Настрой Environment Variables за PostgreSQL

1. Отиди в Database Service dashboard
2. Копирай **Internal Database URL**
3. В Web Service → Environment, добави:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

Или свържи database в Connections tab (Render автоматично добавя `DATABASE_URL`).

### Стъпка 3: Експортирай данните от MySQL

**Локално (ако имаш достъп до MySQL):**

```bash
# Експортирай данните
mysqldump -u username -p database_name > backup.sql

# Или само структурата (schemas)
mysqldump -u username -p --no-data database_name > schema.sql
```

**От Render MySQL (ако имаш достъп):**

```bash
# В Render Shell или локално
mysqldump -h mysql-host -u username -p database_name > backup.sql
```

### Стъпка 4: Приложи миграциите в PostgreSQL

1. В Render Web Service → Shell tab, или локално:
```bash
# Миграциите ще създадат структурата в PostgreSQL
python manage.py migrate
```

### Стъпка 5: Импортирай данните (ако имаш данни)

**Опция A: Използвай Django fixtures (препоръчително)**

```bash
# Експортирай от MySQL
python manage.py dumpdata > data.json

# Импортирай в PostgreSQL
python manage.py loaddata data.json
```

**Опция B: Ръчен импорт (ако имаш много данни)**

1. Конвертирай MySQL dump към PostgreSQL формат
2. Импортирай в PostgreSQL

---

## Вариант 2: Използвай pgloader (Автоматично)

`pgloader` може автоматично да мигрира от MySQL към PostgreSQL.

### Стъпка 1: Инсталирай pgloader

**macOS:**
```bash
brew install pgloader
```

**Linux:**
```bash
sudo apt-get install pgloader
```

### Стъпка 2: Създай миграционен скрипт

Създай файл `migrate.load`:

```sql
LOAD DATABASE
    FROM mysql://username:password@mysql-host:3306/database_name
    INTO postgresql://user:password@postgres-host:5432/database_name

WITH include drop, create tables, create indexes, reset sequences

SET work_mem to '256MB', maintenance_work_mem to '512MB'

CAST type datetime to timestamptz
     drop default drop not null using zero-dates-to-null,
     type date drop not null drop default using zero-dates-to-null,
     type tinyint to boolean using tinyint-to-boolean,
     type year to integer

ALTER TABLE NAMES MATCHING ~/./,
    COLUMNS MATCHING ~/./

BEFORE LOAD DO
    $$ create extension if not exists hstore; $$;
```

### Стъпка 3: Стартирай миграцията

```bash
pgloader migrate.load
```

---

## Вариант 3: Ръчна миграция (За малки бази)

### Стъпка 1: Експортирай данните като JSON

```bash
# От MySQL базата
python manage.py dumpdata > data.json
```

### Стъпка 2: Настрой PostgreSQL

1. Създай PostgreSQL database в Render
2. Добави `DATABASE_URL` в Environment Variables
3. Приложи миграциите:
```bash
python manage.py migrate
```

### Стъпка 3: Импортирай данните

```bash
# В PostgreSQL базата
python manage.py loaddata data.json
```

---

## ⚠️ Важни Бележки

### Разлики между MySQL и PostgreSQL

1. **Auto-increment:**
   - MySQL: `AUTO_INCREMENT`
   - PostgreSQL: `SERIAL` или `BIGSERIAL`
   - Django автоматично го обработва!

2. **Boolean:**
   - MySQL: `TINYINT(1)`
   - PostgreSQL: `BOOLEAN`
   - Django автоматично го конвертира!

3. **Strings:**
   - MySQL: `VARCHAR`
   - PostgreSQL: `VARCHAR` или `TEXT`
   - Работи същото!

4. **Dates:**
   - MySQL: `DATETIME`
   - PostgreSQL: `TIMESTAMP`
   - Django автоматично го обработва!

**Добра новина:** Django ORM скрива всички тези разлики! Просто смени `DATABASE_URL` и миграциите ще работят!

---

## 🚀 Препоръчан Процес

### За нов проект (без данни):

1. Създай PostgreSQL database в Render
2. Добави `DATABASE_URL` в Environment Variables
3. Приложи миграциите: `python manage.py migrate`
4. Готово! ✅

### За съществуваща база с данни:

1. Експортирай данните: `python manage.py dumpdata > data.json`
2. Създай PostgreSQL database в Render
3. Добави `DATABASE_URL` в Environment Variables
4. Приложи миграциите: `python manage.py migrate`
5. Импортирай данните: `python manage.py loaddata data.json`
6. Готово! ✅

---

## 📋 Checklist

- [ ] Експортирал данните от MySQL (ако имаш данни)
- [ ] Създал PostgreSQL database в Render
- [ ] Добавил `DATABASE_URL` в Environment Variables
- [ ] Свързал database в Connections tab
- [ ] Приложил миграциите в PostgreSQL
- [ ] Импортирал данните (ако имаш данни)
- [ ] Тествал приложението

---

## 🔧 След миграцията

### Обнови settings.py (опционално)

Django автоматично детектира PostgreSQL от `DATABASE_URL`, но можеш да провериш:

```python
# В settings.py вече поддържа PostgreSQL автоматично!
# Просто използвай DATABASE_URL
```

### Премахни MySQL variables

След като всичко работи, можеш да премахнеш:
- `MYSQL_HOST`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_PORT`

И използвай само `DATABASE_URL`.

---

## 🆘 Troubleshooting

### Проблем: Foreign key constraints

**Решение:**
```bash
# При loaddata, използвай --natural-foreign
python manage.py loaddata data.json --natural-foreign
```

### Проблем: Encoding issues

**Решение:**
```bash
# Експортирай с правилно encoding
python manage.py dumpdata --natural-foreign --natural-primary > data.json
```

### Проблем: Data too large

**Решение:**
```bash
# Експортирай по apps
python manage.py dumpdata ecommerce > ecommerce_data.json
python manage.py dumpdata auth > auth_data.json
# и т.н.
```

---

**Готово!** Django прави миграцията много лесно - просто смени `DATABASE_URL`! 🎉

