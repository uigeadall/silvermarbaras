# 🚀 Импортирай Данните СЕГА

## Проблем
Базата данни в Railway е празна - таблицата `ecommerce_cartitem` няма данни.

## Решение: Използвай Railway Dashboard

### Стъпка 1: Провери Логовете

1. Отиди на Railway Dashboard: https://railway.app/dashboard
2. Избери проект: **hearty-optimism**
3. Избери service: **marbaras**
4. Отиди на таба **"Logs"**
5. Търси за съобщения като:
   - `📦 Database is empty, importing initial data...`
   - `✅ Data imported successfully!`
   - Или грешки свързани с импорта

### Стъпка 2: Ако автоматичният импорт НЕ е работил

#### Опция A: Използвай Railway CLI (Ако работи)

```bash
cd /Users/antonkondachiev/Desktop/МагазинСребро
railway run python manage.py import_data
```

Това ще изтегли данните от GitHub и ще ги импортира.

#### Опция B: Използвай Railway Dashboard Shell (Ако има)

1. В Railway Dashboard → `marbaras` service
2. Търси опция **"Shell"**, **"Console"**, или **"Terminal"**
3. Ако намериш, изпълни:
   ```bash
   python manage.py import_data
   ```

#### Опция C: Ръчен импорт чрез Railway CLI + MySQL

1. Вземи MySQL credentials от Railway:
   - MySQL service → **"Variables"** tab
   - Копирай: `MYSQLHOST`, `MYSQLPORT`, `MYSQLDATABASE`, `MYSQLUSER`, `MYSQLPASSWORD`

2. Локално, използвай Railway CLI за да се свържеш към MySQL:
   ```bash
   railway connect mysql
   ```

3. В MySQL shell, използвай Django за да импортираш данните (това е сложно, не препоръчвам)

---

## Най-лесен начин: Провери защо автоматичният импорт не работи

1. Отиди на Railway Dashboard → `marbaras` → **"Logs"**
2. Скролни до началото на последния deployment
3. Търси за съобщения свързани с data import
4. Сподели какво виждаш в логовете

---

## Алтернатива: Използвай Railway CLI с правилния начин

Опитай да използваш Railway CLI с правилния service:

```bash
railway run --service marbaras python manage.py import_data
```

Или опитай да използваш Railway CLI за да изтеглиш файла и да го импортираш:

```bash
railway run bash -c "curl -o /tmp/data.json https://raw.githubusercontent.com/uigeadall/marbaras123/newone/data.json && python manage.py loaddata /tmp/data.json"
```

---

## Проверка след импорт

1. Отиди на Railway Dashboard → MySQL service → **"Database"** tab
2. Избери таблица `ecommerce_product`
3. Провери дали има продукти

Или отвори приложението: https://marbaras-production.up.railway.app

---

## Следващи стъпки

Сподели:
1. Какво виждаш в логовете на Railway?
2. Работи ли `railway run python manage.py import_data`?
3. Има ли опция за Shell в Railway Dashboard?

