# 🔧 Поправка на 404 грешка за домейн

## Проблем:
- Railway очаква CNAME за `@` (главен домейн)
- jump.bg не позволява CNAME за главен домейн когато има SOA/NS/MX записи
- Резултат: 404 грешка

## Решение: Използвай само `www` поддомейн

### Стъпка 1: В Railway Dashboard

1. Отиди на **Settings** → **Domains**
2. Намери `marbaras.com` в списъка
3. Кликни на **Delete** (изтрий го)
4. Кликни **"+ Custom Domain"**
5. Въведи: `www.marbaras.com`
6. Railway ще покаже CNAME за `www` (не за `@`)

### Стъпка 2: В jump.bg DNS мениджъра

1. Убеди се че CNAME за `www` сочи към: `1f4goo74.up.railway.app`
2. Ако не е така, редактирай го:
   - Хост: `www`
   - Тип: `CNAME`
   - Стойност: `1f4goo74.up.railway.app`
   - Запази промените

### Стъпка 3: Добави домейните в Railway Variables

1. Отиди на **Settings** → **Variables**
2. Добави/редактирай `DJANGO_ALLOWED_HOSTS`:
   ```
   www.marbaras.com,marbaras-production.up.railway.app
   ```
3. Добави/редактирай `CSRF_TRUSTED_ORIGINS`:
   ```
   https://www.marbaras.com,https://marbaras-production.up.railway.app
   ```
4. Убеди се че `DJANGO_DEBUG` е `False`

### Стъпка 4: Изчакай

1. Изчакай 5-15 минути за DNS да се разпространи
2. Railway автоматично ще redeploy-не след промяна на Variables
3. Провери в Railway → Settings → Domains дали `www.marbaras.com` е "Active"

### Стъпка 5: Тествай

1. Отиди на `https://www.marbaras.com`
2. Трябва да видиш сайта
3. Ако все още има 404, провери Railway logs за грешки

---

## За главен домейн (`marbaras.com`)

Ако искаш и `marbaras.com` (без www) да работи, можеш да:

1. **Направиш redirect в Django** (ще добавим код за това)
2. **Използваш jump.bg redirect** (ако поддържат)

Засега фокусирай се на `www.marbaras.com` - това е по-лесно и ще работи веднага.

