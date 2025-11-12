# 📤 Експортиране на Данни от Render MySQL

## Проблем

Получаваш грешка:
```
Can't connect to local MySQL server through socket '/tmp/mysql.sock' (2)
```

**Причина:** Django се опитва да се свърже с локален MySQL, но трябва да се свърже с Render MySQL базата.

---

## Решение 1: Експортирай директно от Render Shell

### Стъпка 1: Отвори Shell в Render

1. В Render Dashboard → Web Service → "Shell" tab
2. Това отваря терминал в твоя container

### Стъпка 2: Експортирай данните

В Render Shell:
```bash
python manage.py dumpdata > data.json
```

Това ще работи защото в Render environment variables са правилно настроени!

### Стъпка 3: Изтегли файла

Render Shell не позволява директно download, така че:

**Опция A: Копирай съдържанието**
```bash
cat data.json
```
Копирай output-а и запази го локално като `data.json`

**Опция B: Използвай Render API или друг метод**

---

## Решение 2: Настрой локално .env за да се свържеш с Render MySQL

### Стъпка 1: Вземи MySQL Connection Details от Render

1. Отиди в Render Dashboard → Database Service (MySQL)
2. Копирай:
   - **External Connection** string (за локално използване)
   - Или отделните параметри: Host, Port, Database, User, Password

### Стъпка 2: Създай/Обнови .env файл локално

В root директорията на проекта, създай/обнови `.env` файл:

```env
# MySQL Connection (от Render)
MYSQL_HOST=your-mysql-host.onrender.com
MYSQL_PORT=3306
MYSQL_DATABASE=your_database_name
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password

# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### Стъпка 3: Експортирай локално

```bash
python3 manage.py dumpdata > data.json
```

---

## Решение 3: Използвай mysqldump директно

### Стъпка 1: Инсталирай MySQL client

**macOS:**
```bash
brew install mysql-client
```

**Linux:**
```bash
sudo apt-get install mysql-client
```

### Стъпка 2: Експортирай с mysqldump

```bash
mysqldump -h your-mysql-host.onrender.com \
  -P 3306 \
  -u your_username \
  -p \
  your_database_name > backup.sql
```

Въведи паролата когато се поиска.

**Забележка:** Това експортира SQL формат, не JSON. За да импортираш в PostgreSQL, ще трябва да конвертираш или да използваш друг метод.

---

## Решение 4: Пропусни експорта (ако нямаш данни)

**Ако базата е празна или нямаш важни данни:**

1. Просто пропусни експорта
2. Създай PostgreSQL database в Render
3. Приложи миграциите
4. Готово!

---

## Препоръчан Процес

### Ако имаш данни:

1. **Най-лесно:** Използвай Render Shell
   - Отиди в Shell tab
   - `python manage.py dumpdata > data.json`
   - Копирай съдържанието

2. **Алтернатива:** Настрой локално .env с Render MySQL credentials
   - Създай .env файл
   - Добави MySQL connection details
   - `python3 manage.py dumpdata > data.json`

### Ако нямаш данни:

1. Пропусни експорта
2. Създай PostgreSQL database
3. Приложи миграциите
4. Готово!

---

## След експорта

След като имаш `data.json`:

1. Създай PostgreSQL database в Render
2. Свържи го в Connections tab
3. Приложи миграциите: `python manage.py migrate`
4. Импортирай данните: `python manage.py loaddata data.json`

---

## ⚠️ Важно

- **Render External Connection** работи само от whitelisted IPs
- Може да се наложи да whitelist-неш твоя IP в Render database settings
- Или използвай Render Shell (най-лесно)

---

**Най-лесно е да използваш Render Shell за експорт!** 🎉

