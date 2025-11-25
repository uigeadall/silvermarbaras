# 🔧 Обновяване на CNAME за www с нова Railway стойност

## Нова Railway CNAME стойност:
Railway сега очаква: `rlvxys18.up.railway.app` (нова стойност)

## Стъпка: Обнови CNAME за www

1. Отиди на jump.bg DNS мениджъра
2. Намери CNAME запис за `www`
3. Редактирай стойността:
   - Хост: `www` (без точка в края)
   - Тип: `CNAME`
   - Стойност: `rlvxys18.up.railway.app` (БЕЗ точка в края)
   - TTL: `14400` или `3600`
4. **ВАЖНО:** Кликни **"Запази промените"** (син бутон)

## За root domain (@):

Railway очаква CNAME за `@` (root domain), но jump.bg не позволява CNAME за root domain когато има други записи (SOA, NS, MX).

**Решение:**
- Остави A запис за `marbaras.com.` както е (`66.33.22.165`)
- Railway може да показва грешка за root domain, но `www.marbaras.com` ще работи

## След запазване:

1. Изчакай 10-15 минути
2. Отиди на Railway → Settings → Domains
3. Намери `www.marbaras.com`
4. Кликни **"Check DNS"** бутона
5. Railway трябва да покаже "Active" (зелена отметка)

## Проверка:

След промяната:

```bash
# Проверка на CNAME (трябва да видиш новата Railway стойност)
dig www.marbaras.com CNAME +short
```

**Очакван резултат:** `rlvxys18.up.railway.app.`

---

## Важно:

- Railway може да показва грешка "Incorrect value 'marbaras.com'" за root domain
- Това е нормално, защото jump.bg не позволява CNAME за root domain
- `www.marbaras.com` ще работи въпреки грешката за root domain
- Тествай в браузър: `https://www.marbaras.com`

---

## Ако Railway все още показва грешка:

1. Убеди се че CNAME за `www` е точно `rlvxys18.up.railway.app`
2. Убеди се че си запазил промените в jump.bg
3. Изчакай още 30 минути за DNS да се разпространи
4. Тествай в браузър: `https://www.marbaras.com` (може да работи въпреки грешката в Railway)

