# 🔧 Поправка на root domain DNS (Railway очаква CNAME за @)

## Проблем:
Railway очаква CNAME за root domain (`@`) със стойност `ej8fghaw.up.railway.app`, но:
- jump.bg не позволява CNAME за root domain когато има други записи (SOA, NS, MX)
- В jump.bg има A запис за `marbaras.com.` който сочи към `37.59.128.128` (стар IP)

## Решение: Използвай A запис за root domain сочещ към Railway IP

### Стъпка 1: Намери Railway IP адрес

Railway CNAME `ej8fghaw.up.railway.app` сочи към IP адрес. Трябва да намерим този IP.

**Опция 1: Използвай команда:**
```bash
dig ej8fghaw.up.railway.app A +short
```

**Опция 2: Провери в Railway:**
1. Railway може да покаже IP адрес в настройките
2. Или използвай онлайн DNS checker: https://dnschecker.org/
   - Въведи: `ej8fghaw.up.railway.app`
   - Тип: `A`
   - Копирай IP адреса

### Стъпка 2: Обнови A запис за root domain в jump.bg

1. Отиди на jump.bg DNS мениджъра
2. Намери A запис за `marbaras.com.` (root domain)
3. Редактирай стойността да сочи към Railway IP адрес (от Стъпка 1)
4. Убеди се че:
   - Хост: `marbaras.com.` (с точка в края)
   - Тип: `A`
   - Стойност: **[Railway IP адрес]** (напр. `66.33.22.165`)
   - TTL: `14400` или `3600`
5. **ВАЖНО:** Кликни **"Запази промените"**

### Стъпка 3: Обнови CNAME за www

1. В същия DNS мениджър, намери CNAME за `www`
2. Редактирай стойността да сочи към: `ej8fghaw.up.railway.app`
3. Убеди се че:
   - Хост: `www` (без точка в края)
   - Тип: `CNAME`
   - Стойност: `ej8fghaw.up.railway.app` (без точка в края)
4. **ВАЖНО:** Кликни **"Запази промените"**

### Стъпка 4: Провери в Railway

1. Отиди на Railway → Settings → Domains
2. Намери `www.marbaras.com`
3. Кликни **"Check DNS"** бутона
4. Изчакай 1-2 минути
5. Railway трябва да покаже "Active" (зелена отметка)

### Стъпка 5: Ако Railway все още показва грешка

Railway може да очаква CNAME за root domain, но jump.bg не позволява това. В този случай:

**Вариант A: Използвай само www (препоръчително)**
- Остави A запис за root domain както е (може да сочи към стар сървър)
- Railway ще работи само с `www.marbaras.com`
- `marbaras.com` (без www) може да не работи, но `www.marbaras.com` ще работи

**Вариант B: Използвай Railway IP за root domain**
- Обнови A запис за `marbaras.com.` да сочи към Railway IP
- Това ще направи и root domain да работи

---

## Важно:

- Railway може да показва грешка за root domain, но `www.marbaras.com` може да работи въпреки това
- Тествай в браузър: `https://www.marbaras.com`
- Ако работи, можеш да игнорираш грешката за root domain

---

## Проверка:

След промените:

```bash
# Проверка на A запис за root domain
dig marbaras.com A +short

# Проверка на CNAME за www
dig www.marbaras.com CNAME +short

# Проверка на Railway CNAME
dig ej8fghaw.up.railway.app A +short
```

---

## Ако все още има проблеми:

1. Провери дали си запазил промените в jump.bg
2. Използвай DNS Checker за глобална проверка
3. Тествай в браузър: `https://www.marbaras.com`
4. Ако сайтът работи, Railway грешката може да се игнорира

