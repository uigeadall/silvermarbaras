# 📥 Импортиране на данни в Railway MySQL

## ✅ Стъпка 1: Данните са експортирани!

Файлът `data.json` (816KB) е готов и съдържа всички данни от локалната MySQL база.

---

## Стъпка 2: Свържи MySQL към Web Service в Railway

### В Railway Dashboard:

1. **Architecture View** → Виж дали имаш:
   - ✅ `marbaras` (Web Service)
   - ✅ `MySQL` (Database Service)

2. **Свържи MySQL към Web Service:**
   - Click на **MySQL** service
   - Отиди на **"Settings"** tab
   - Търси **"Connect"** или **"Add to Project"** бутон
   - Click и избери **`marbaras`** web service
   - Railway автоматично добавя `DATABASE_URL`!

3. **Провери DATABASE_URL:**
   - Click на **`marbaras`** web service
   - Отиди на **"Variables"** tab
   - Трябва да видиш:
     ```
     DATABASE_URL=mysql://user:password@host:3306/database
     ```
   - **Важно:** Трябва да започва с `mysql://`, НЕ `postgresql://`!

---

## Стъпка 3: Премахни PostgreSQL (ако не го използваш)

Ако имаш `marbaras-db` (PostgreSQL) и не го използваш:

1. Click на **`marbaras-db`** service
2. **Settings** → Scroll down → **"Danger Zone"**
3. Click **"Delete Service"**

Това ще премахне объркването.

---

## Стъпка 4: Импортирай данните в Railway MySQL

### Опция A: Използвай Railway CLI (Препоръчително)

```bash
# Инсталирай Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link към проекта
cd /Users/antonkondachiev/Desktop/МагазинСребро
railway link

# Избери проекта и service (marbaras)

# Приложи миграциите първо
railway run python manage.py migrate

# Импортирай данните
railway run python manage.py loaddata data.json
```

### Опция B: Използвай Railway Shell (Алтернатива)

1. В Railway Dashboard → `marbaras` service → **"Shell"** tab
2. В shell терминала:
   ```bash
   # Приложи миграциите първо
   python manage.py migrate
   
   # Създай data.json файл
   nano data.json
   ```
3. Постави съдържанието от локалния `data.json` файл
4. Save: `Ctrl+O`, `Enter`, `Ctrl+X`
5. Импортирай:
   ```bash
   python manage.py loaddata data.json
   ```

### Опция C: Качи файла чрез Railway Deploy

1. Убеди се че `data.json` е в проекта (вече е там!)
2. Railway автоматично ще го качи при следващия deploy
3. След deploy, използвай Railway Shell:
   ```bash
   python manage.py migrate
   python manage.py loaddata data.json
   ```

---

## Стъпка 5: Провери че всичко работи

1. В Railway Dashboard → `marbaras` service → **"Logs"** tab
2. Провери дали има грешки
3. Отвори приложението в браузъра
4. Провери дали продуктите са там!

---

## Troubleshooting

### Проблем: Foreign key constraints

**Решение:**
```bash
python manage.py loaddata data.json --natural-foreign --natural-primary
```

### Проблем: DATABASE_URL все още сочи към PostgreSQL

**Решение:**
1. Провери дали `DATABASE_URL` започва с `mysql://` (НЕ `postgresql://`)
2. Премахни всички `POSTGRES_*` environment variables
3. Премахни PostgreSQL service (ако не го използваш)
4. Redeploy web service

### Проблем: "No such file: data.json"

**Решение:**
- Убеди се че файлът е в root директорията на проекта
- Или използвай пълен път: `python manage.py loaddata /app/data.json`

---

## Резюме

1. ✅ Данните са експортирани (`data.json` - 816KB)
2. ⏳ Свържи MySQL service към `marbaras` web service в Railway
3. ⏳ Провери че `DATABASE_URL` започва с `mysql://`
4. ⏳ Импортирай данните: `python manage.py loaddata data.json`
5. ⏳ Премахни PostgreSQL service (ако не го използваш)
6. ⏳ Готово! 🎉

---

## Следващи стъпки

След като всичко работи:
- [ ] Тествай приложението
- [ ] Провери дали продуктите са там
- [ ] Настрой други environment variables (Stripe, Email, etc.)

