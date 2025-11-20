# 🔧 Поправка на Railway DNS проверка

## Проблем:
Railway все още показва "Incorrect DNS setup" защото проверява за CNAME на `@` вместо на `www`.

## Решение: Изтрий и добави отново домейна в Railway

### Стъпка 1: Изтрий домейна в Railway

1. Отиди на **Railway Dashboard** → **Settings** → **Domains**
2. Намери `marbaras.com` или `www.marbaras.com` в списъка
3. Кликни на **Delete** (изтрий го)
4. Потвърди изтриването

### Стъпка 2: Добави отново само `www.marbaras.com`

1. В същата страница, кликни **"+ Custom Domain"**
2. Въведи: `www.marbaras.com` (само www, не главен домейн)
3. Railway ще покаже CNAME запис за `www` (не за `@`)
4. Копирай стойността (напр. `sn6khg43.up.railway.app`)

### Стъпка 3: Провери DNS в jump.bg

1. Отиди на jump.bg DNS мениджъра
2. Убеди се че CNAME за `www` сочи към правилната стойност от Railway
3. Ако не е така, редактирай го:
   - Хост: `www`
   - Тип: `CNAME`
   - Стойност: `sn6khg43.up.railway.app` (или каквото Railway покаже)
   - Запази промените

### Стъпка 4: Провери Variables в Railway

1. Отиди на **Settings** → **Variables**
2. Убеди се че имаш:
   - `DJANGO_ALLOWED_HOSTS` = `www.marbaras.com,marbaras-production.up.railway.app`
   - `CSRF_TRUSTED_ORIGINS` = `https://www.marbaras.com,https://marbaras-production.up.railway.app`
   - `DJANGO_DEBUG` = `False`

### Стъпка 5: Изчакай DNS да се разпространи

1. Изчакай 10-15 минути
2. Railway автоматично ще провери DNS след няколко минути
3. Провери в Railway → Settings → Domains дали `www.marbaras.com` е "Active" (зелена отметка)

### Стъпка 6: Тествай

1. Отиди на `https://www.marbaras.com`
2. Трябва да видиш сайта
3. Ако отидеш на `https://marbaras.com` (без www), автоматично ще те пренасочи към `www.marbaras.com`

---

## Ако все още има проблеми:

1. Провери Railway logs за грешки
2. Използвай [DNS Checker](https://dnschecker.org/) за да провериш дали DNS е разпространен:
   - Въведи: `www.marbaras.com`
   - Тип: `CNAME`
   - Провери дали всички сървъри показват правилната стойност

3. Сподели:
   - Какво показва Railway → Settings → Domains
   - Какво показва DNS Checker
   - Какви грешки виждаш в браузъра

