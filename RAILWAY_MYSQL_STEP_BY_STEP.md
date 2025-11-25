# 🚀 Пълно Ръководство: MySQL в Railway - Стъпка по Стъпка

## ✅ Стъпка 1: Данните са готови!

Файлът `data.json` (816KB) е експортиран и готов за импортиране.

---

## Стъпка 2: Свържи MySQL към Web Service в Railway

### 2.1. Отвори Railway Dashboard

1. Отиди на [railway.app](https://railway.app)
2. Login с твоя акаунт
3. Избери проекта **"hearty-optimism"** (или както се казва)

### 2.2. Провери Architecture View

1. В Railway Dashboard → Click на **"Architecture"** tab (отгоре)
2. Трябва да видиш:
   - ✅ `marbaras` (Web Service) - зелена галочка
   - ✅ `MySQL` (Database Service) - зелена галочка
   - ⚠️ `marbaras-db` (PostgreSQL) - ако го виждаш, ще го премахнем

### 2.3. Свържи MySQL към Web Service

**Вариант A: Чрез Architecture View (Най-лесно)**

1. В Architecture view, виж дали има **линия** между `MySQL` и `marbaras`
2. Ако **НЯМА** линия:
   - Hover над `MySQL` service card
   - Трябва да видиш малък **"+"** или **"Connect"** бутон
   - Click на него
   - Избери `marbaras` web service
   - Railway автоматично добавя `DATABASE_URL`!

**Вариант B: Чрез Settings (Алтернатива)**

1. Click на **`MySQL`** service card
2. Отиди на **"Settings"** tab
3. Scroll down до секцията **"Connections"** или **"Variables"**
4. Трябва да видиш **"Connect"** или **"Add to Project"** бутон
5. Click и избери **`marbaras`** web service
6. Railway автоматично добавя `DATABASE_URL`!

---

## Стъпка 3: Провери DATABASE_URL

### 3.1. Отвори Variables на Web Service

1. Click на **`marbaras`** web service card
2. Отиди на **"Variables"** tab (отгоре)
3. Търси **`DATABASE_URL`** в списъка

### 3.2. Провери Формата

`DATABASE_URL` трябва да изглежда така:

```
DATABASE_URL=mysql://user:password@host:3306/database
```

**Важно:**
- ✅ Трябва да започва с `mysql://`
- ❌ НЕ трябва да започва с `postgresql://`

### 3.3. Ако НЯМА DATABASE_URL

Ако не виждаш `DATABASE_URL`:
- MySQL не е свързан към web service
- Върни се на Стъпка 2.3 и свържи MySQL отново

---

## Стъпка 4: Премахни PostgreSQL (Ако не го използваш)

### 4.1. Провери дали имаш PostgreSQL

В Architecture view, провери дали виждаш:
- `marbaras-db` (PostgreSQL service)

### 4.2. Ако имаш PostgreSQL и не го използваш:

1. Click на **`marbaras-db`** service card
2. Отиди на **"Settings"** tab
3. Scroll down до **"Danger Zone"** (в долната част)
4. Click на **"Delete Service"** бутон
5. Потвърди изтриването

**Забележка:** Това ще изтрие PostgreSQL базата и всички данни в нея. Ако имаш важни данни там, първо ги експортирай!

---

## Стъпка 5: Импортирай данните в Railway MySQL

### 5.1. Инсталирай Railway CLI (Ако нямаш)

**macOS:**
```bash
npm i -g @railway/cli
```

**Или с Homebrew:**
```bash
brew install railway
```

### 5.2. Login в Railway CLI

```bash
railway login
```

Това ще отвори браузър за автентикация.

### 5.3. Link към проекта

```bash
cd /Users/antonkondachiev/Desktop/МагазинСребро
railway link
```

Това ще те попита:
- "Select a project" → Избери **"hearty-optimism"** (или както се казва)
- "Select a service" → Избери **"marbaras"** (web service)

### 5.4. Приложи миграциите първо

```bash
railway run python manage.py migrate
```

Това ще създаде структурата на базата данни в Railway MySQL.

### 5.5. Импортирай данните

```bash
railway run python manage.py loaddata data.json
```

Това ще импортира всички данни от `data.json` в Railway MySQL.

**Очакван output:**
```
Installed X object(s) from 1 fixture(s)
```

---

## Стъпка 6: Провери че всичко работи

### 6.1. Провери Logs

1. В Railway Dashboard → `marbaras` service → **"Logs"** tab
2. Провери дали има грешки
3. Трябва да видиш: "Starting Gunicorn..." и "Booting worker..."

### 6.2. Отвори приложението

1. В Railway Dashboard → `marbaras` service → **"Settings"** tab
2. Търси **"Domains"** или **"Public URL"**
3. Click на URL-а или копирай го
4. Отвори в браузър

### 6.3. Провери продуктите

1. Отиди на страницата с продукти
2. Провери дали виждаш продуктите от локалната база
3. Ако виждаш продуктите → ✅ Успех!

---

## Troubleshooting

### Проблем: "Command not found: railway"

**Решение:**
```bash
npm i -g @railway/cli
# Или
brew install railway
```

### Проблем: "No such file: data.json"

**Решение:**
Убеди се че `data.json` е в root директорията:
```bash
cd /Users/antonkondachiev/Desktop/МагазинСребро
ls -la data.json
```

Ако файлът не е там, Railway CLI няма да го намери.

### Проблем: "Foreign key constraint fails"

**Решение:**
```bash
railway run python manage.py loaddata data.json --natural-foreign --natural-primary
```

### Проблем: DATABASE_URL все още сочи към PostgreSQL

**Решение:**
1. Провери дали `DATABASE_URL` започва с `mysql://` (НЕ `postgresql://`)
2. Премахни всички `POSTGRES_*` environment variables от Variables tab
3. Премахни PostgreSQL service (ако не го използваш)
4. Redeploy web service:
   - `marbaras` service → **"Deployments"** tab → **"Redeploy"**

### Проблем: "Can't connect to MySQL"

**Решение:**
1. Провери дали MySQL service е running (зелена галочка)
2. Провери дали `DATABASE_URL` е правилно настроен
3. Провери дали MySQL е свързан към web service (трябва да има линия в Architecture view)

---

## Алтернатива: Използвай Railway Shell (Без CLI)

Ако не искаш да инсталираш Railway CLI:

### 5.1. Отвори Railway Shell

1. В Railway Dashboard → `marbaras` service → **"Shell"** tab
2. Това отваря терминал в твоя container

### 5.2. Качи data.json файла

**Проблем:** Railway Shell не позволява директно upload на файлове.

**Решение:** Копирай съдържанието на `data.json`:

1. Локално, отвори `data.json`:
   ```bash
   cat data.json
   ```
2. Копирай цялото съдържание
3. В Railway Shell:
   ```bash
   nano data.json
   ```
4. Постави съдържанието (Cmd+V или Ctrl+V)
5. Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### 5.3. Приложи миграциите и импортирай

```bash
python manage.py migrate
python manage.py loaddata data.json
```

---

## Резюме - Бърз Списък

1. ✅ Данните са експортирани (`data.json`)
2. ⏳ Railway Dashboard → Architecture → Свържи MySQL към `marbaras`
3. ⏳ Провери `DATABASE_URL` в Variables (трябва да започва с `mysql://`)
4. ⏳ Премахни PostgreSQL service (ако не го използваш)
5. ⏳ `railway login` и `railway link`
6. ⏳ `railway run python manage.py migrate`
7. ⏳ `railway run python manage.py loaddata data.json`
8. ⏳ Провери приложението в браузър

---

## Следващи стъпки

След като всичко работи:
- [ ] Тествай приложението
- [ ] Провери дали продуктите са там
- [ ] Настрой други environment variables (Stripe, Email, etc.)
- [ ] Настрой custom domain (ако искаш)

---

**Готово!** Следвай стъпките една по една и всичко ще работи! 🎉

