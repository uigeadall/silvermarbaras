# 📥 Импортиране на Данни в Railway MySQL

## ✅ Deploy Успешен!

Приложението е deployed и работи! Сега трябва да импортираме данните от `data.json` в Railway MySQL.

---

## Стъпка 1: Инсталирай Railway CLI

**macOS:**
```bash
npm i -g @railway/cli
```

**Или с Homebrew:**
```bash
brew install railway
```

---

## Стъпка 2: Login в Railway CLI

```bash
railway login
```

Това ще отвори браузър за автентикация. Login с твоя Railway акаунт.

---

## Стъпка 3: Link към проекта

```bash
cd /Users/antonkondachiev/Desktop/МагазинСребро
railway link
```

Това ще те попита:
- "Select a project" → Избери **"hearty-optimism"**
- "Select a service" → Избери **"marbaras"**

---

## Стъпка 4: Приложи миграциите първо

```bash
railway run python manage.py migrate
```

Това ще създаде структурата на базата данни в Railway MySQL.

**Очакван output:**
```
Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying ecommerce.0001_initial... OK
  ...
```

---

## Стъпка 5: Импортирай данните

```bash
railway run python manage.py loaddata data.json
```

Това ще импортира всички данни от `data.json` в Railway MySQL.

**Очакван output:**
```
Installed X object(s) from 1 fixture(s)
```

---

## Стъпка 6: Провери че данните са импортирани

### Опция A: Чрез Railway Shell

```bash
railway run python manage.py shell
```

В Python shell:
```python
from ecommerce.models import Product
print(f"Total products: {Product.objects.count()}")
```

### Опция B: Чрез приложението

1. Отвори приложението в браузър:
   ```
   https://marbaras-production.up.railway.app
   ```
2. Провери дали виждаш продуктите от локалната база

---

## Troubleshooting

### Проблем: "Command not found: railway"

**Решение:**
```bash
npm i -g @railway/cli
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

### Проблем: "Database connection error"

**Решение:**
1. Провери дали `DATABASE_URL` е правилен в Railway Variables
2. Провери дали MySQL service е Active
3. Провери Deploy Logs за грешки

---

## Резюме

1. ✅ Deploy успешен
2. ⏳ Инсталирай Railway CLI: `npm i -g @railway/cli`
3. ⏳ Login: `railway login`
4. ⏳ Link: `railway link`
5. ⏳ Миграции: `railway run python manage.py migrate`
6. ⏳ Импортирай данните: `railway run python manage.py loaddata data.json`
7. ⏳ Провери приложението в браузър

---

**Готово! Следвай стъпките една по една!** 🎉

