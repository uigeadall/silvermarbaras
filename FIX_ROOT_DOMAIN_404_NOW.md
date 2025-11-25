# 🔧 Поправка на 404 за marbaras.com (без www)

## Проблем:
`marbaras.com` (без www) показва 404 грешка, докато `www.marbaras.com` работи.

## Причина:
Railway може да не обслужва root domain (`marbaras.com`) правилно, защото:
- Railway очаква CNAME за root domain (`@`)
- Но jump.bg не позволява CNAME за root domain когато има други записи (SOA, NS, MX)
- В jump.bg има A запис за root domain (`66.33.22.165`), но Railway може да не го приема правилно

## Решение 1: Добави root domain в Railway

1. Отиди на **Railway Dashboard** → **Settings** → **Networking** (или **Domains**)
2. Кликни **"+ Custom Domain"**
3. Въведи: `marbaras.com` (без www)
4. Railway ще покаже какво очаква за DNS

**ВАЖНО:** Railway вероятно ще покаже че очаква CNAME за `@` (root domain), но jump.bg не позволява това.

## Решение 2: Провери дали Railway обслужва root domain

1. Отиди на Railway → Settings → Domains
2. Провери дали имаш само `www.marbaras.com` или и двата домейна
3. Ако имаш само `www.marbaras.com`:
   - Railway не обслужва root domain
   - Това е причината за 404

## Решение 3: Ако Railway не обслужва root domain

Ако Railway не може да обслужва root domain (защото очаква CNAME, но jump.bg не позволява):

### Опция A: Използвай само www (препоръчително)
- Остави само `www.marbaras.com` в Railway
- Потребителите трябва да използват `www.marbaras.com`
- Това е най-често срещаното решение

### Опция B: Добави root domain в Railway с A запис
1. Добави `marbaras.com` в Railway
2. Railway може да покаже грешка за DNS
3. Но ако A записът сочи към правилния Railway IP, може да работи

### Опция C: Използвай друг DNS provider
Ако искаш root domain да работи правилно:
1. Използвай DNS provider който позволява CNAME за root domain (напр. Cloudflare)
2. Промени nameservers-ите на домейна да сочат към новия DNS provider
3. След това можеш да добавиш CNAME за `@` както Railway очаква

## Проверка:

1. Тествай `https://www.marbaras.com` - трябва да работи ✅
2. Тествай `https://marbaras.com` - може да не работи (това е нормално ако Railway не обслужва root domain)

## Важно:

- `www.marbaras.com` трябва да работи правилно ✅
- `marbaras.com` (без www) може да не работи ако Railway не обслужва root domain
- Това е нормално ограничение когато Railway очаква CNAME за root domain, но DNS provider не позволява това

## Следващи стъпки:

1. Провери Railway → Settings → Domains дали имаш `marbaras.com` (без www)
2. Ако няма, опитай да го добавиш
3. Ако Railway показва грешка за DNS, но A записът е правилен (`66.33.22.165`), може да работи въпреки грешката
4. Тествай `https://marbaras.com` след добавяне на домейна в Railway

