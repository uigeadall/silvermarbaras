# 🔧 Поправка на Railway root domain проблем

## Проблем:
Railway очаква CNAME за root domain (`@`) със стойност `rlvxys18.up.railway.app`, но:
- jump.bg не позволява CNAME за root domain когато има други записи (SOA, NS, MX)
- В jump.bg има A запис за root domain (`marbaras.com.` → `66.33.22.165`), не CNAME

## Решение: Използвай само www поддомейн

### Стъпка 1: Остави DNS записите както са

В jump.bg:
- Остави A запис за `marbaras.com.` → `66.33.22.165` (Railway IP)
- Остави CNAME за `www` → `rlvxys18.up.railway.app` (Railway CNAME)

### Стъпка 2: Railway може да показва грешка, но www ще работи

Railway може да показва "Incorrect DNS setup" за root domain, но `www.marbaras.com` ще работи правилно защото:
- CNAME за `www` е правилно конфигуриран
- Railway обслужва `www` поддомейна правилно

### Стъпка 3: Изчакай DNS разпространение

1. Изчакай 30-60 минути за DNS да се разпространи
2. Провери в DNS Checker: https://dnschecker.org/
3. Убеди се че CNAME за `www` сочи към `rlvxys18.up.railway.app`

### Стъпка 4: Тествай www.marbaras.com

1. Отиди на `https://www.marbaras.com`
2. Трябва да работи правилно
3. Railway може да показва грешка за root domain, но това не пречи на `www`

---

## Алтернативно решение: Използвай друг DNS provider

Ако искаш root domain да работи правилно:

1. Използвай DNS provider който позволява CNAME за root domain (напр. Cloudflare)
2. Промени nameservers-ите на домейна да сочат към новия DNS provider
3. Добави CNAME за `@` със стойност `rlvxys18.up.railway.app`

---

## Важно:

- Railway може да показва "Incorrect DNS setup" за root domain, но `www.marbaras.com` ще работи
- Това е нормално ограничение когато DNS provider не позволява CNAME за root domain
- Повечето сайтове използват само `www` поддомейн

---

## Проверка:

След 30-60 минути:

1. Тествай `https://www.marbaras.com` - трябва да работи
2. Railway може да показва грешка за root domain, но това не пречи на `www`
3. Провери DNS Checker за CNAME на `www` - трябва да показва `rlvxys18.up.railway.app`

---

## Ако искаш root domain да работи:

1. Използвай Cloudflare или друг DNS provider който позволява CNAME за root domain
2. Промени nameservers-ите на домейна
3. Добави CNAME за `@` със стойност `rlvxys18.up.railway.app`

