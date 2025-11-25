# 🔧 Поправка на 404 за marbaras.com (без www)

## Проблем:
`marbaras.com` (без www) показва 404 грешка от LiteSpeed Web Server.

## Причина:
Railway може да не обслужва root domain (`marbaras.com`) правилно, защото:
- Railway очаква CNAME за root domain (`@`)
- Но jump.bg не позволява CNAME за root domain когато има други записи (SOA, NS, MX)
- В jump.bg има A запис за root domain, но Railway може да не го приема правилно

## Решение:

### Стъпка 1: Тествай www.marbaras.com

1. Отиди на `https://www.marbaras.com` (с www)
2. Ако този работи:
   - Проблемът е само с root domain
   - Railway обслужва само `www` поддомейна

### Стъпка 2: Провери Railway Domains

1. Отиди на Railway → Settings → Domains
2. Провери дали имаш само `www.marbaras.com` или и двата домейна
3. Ако имаш само `www.marbaras.com`:
   - Това е нормално - Railway обслужва само www
   - Root domain може да не работи

### Стъпка 3: Поправи middleware редирект

Има `WWWRedirectMiddleware` който трябва да редиректва `marbaras.com` към `www.marbaras.com`, но ако Railway не обслужва root domain, редиректът няма да работи.

**Решение:** Railway трябва да обслужва root domain за да работи редиректът.

### Стъпка 4: Добави root domain в Railway (ако е необходимо)

1. Отиди на Railway → Settings → Domains
2. Кликни "+ Custom Domain"
3. Въведи: `marbaras.com` (без www)
4. Railway ще покаже CNAME за `@` (root domain)
5. Но jump.bg не позволява CNAME за root domain

**Проблем:** Railway очаква CNAME за `@`, но jump.bg не позволява това.

---

## Алтернативно решение: Използвай само www

Ако Railway не може да обслужва root domain правилно:

1. Остави само `www.marbaras.com` в Railway
2. Остави A запис за `marbaras.com.` в jump.bg (може да сочи към стар сървър или Railway IP)
3. Потребителите трябва да използват `www.marbaras.com`

**За редирект от root domain:**
- Може да се направи на ниво DNS (но това не винаги работи)
- Или на ниво Railway (но трябва Railway да обслужва root domain)

---

## Проверка:

1. Тествай `https://www.marbaras.com` - трябва да работи
2. Тествай `https://marbaras.com` - може да не работи (това е нормално ако Railway не обслужва root domain)

---

## Важно:

- `www.marbaras.com` трябва да работи правилно
- `marbaras.com` (без www) може да не работи ако Railway не обслужва root domain
- Това е нормално ограничение когато Railway очаква CNAME за root domain, но DNS provider не позволява това

---

## Ако искаш root domain да работи:

1. Провери дали Railway поддържа A записи за root domain (не само CNAME)
2. Ако не, може да използваш друг DNS provider който позволява CNAME за root domain
3. Или използвай само `www.marbaras.com` (което е по-често срещано)

