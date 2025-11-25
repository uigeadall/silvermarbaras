# 🔧 Поправка на 404 грешка за www.marbaras.com

## Проблем:
Получаваш 404 грешка когато отваряш `https://www.marbaras.com`.

## Причини:
1. `DJANGO_ALLOWED_HOSTS` не включва `www.marbaras.com`
2. `CSRF_TRUSTED_ORIGINS` не е настроен правилно
3. DNS все още не се е разпространил напълно

## Решение:

### Стъпка 1: Провери Railway Variables

1. Отиди на **Railway Dashboard** → **Settings** → **Variables**
2. Провери дали имаш следните variables:

#### `DJANGO_ALLOWED_HOSTS`
Трябва да съдържа:
```
www.marbaras.com,marbaras-production.up.railway.app
```

**Ако няма или е неправилно:**
1. Кликни **"+ New Variable"** (или редактирай съществуващия)
2. Име: `DJANGO_ALLOWED_HOSTS`
3. Стойност: `www.marbaras.com,marbaras-production.up.railway.app`
4. Запази

#### `CSRF_TRUSTED_ORIGINS`
Трябва да съдържа:
```
https://www.marbaras.com,https://marbaras-production.up.railway.app
```

**Ако няма или е неправилно:**
1. Кликни **"+ New Variable"** (или редактирай съществуващия)
2. Име: `CSRF_TRUSTED_ORIGINS`
3. Стойност: `https://www.marbaras.com,https://marbaras-production.up.railway.app`
4. Запази

#### `DJANGO_DEBUG`
Трябва да е:
```
False
```

**Ако е `True` или няма:**
1. Кликни **"+ New Variable"** (или редактирай съществуващия)
2. Име: `DJANGO_DEBUG`
3. Стойност: `False`
4. Запази

### Стъпка 2: Изчакай Railway да redeploy-не

1. След като промениш Variables, Railway автоматично ще redeploy-не приложението
2. Изчакай 2-3 минути
3. Провери Railway logs за грешки

### Стъпка 3: Провери DNS разпространение

1. Отиди на: https://dnschecker.org/
2. Въведи: `www.marbaras.com`
3. Тип: `CNAME`
4. Провери дали всички сървъри показват `rlvxys18.up.railway.app`

**Ако някои сървъри все още показват стара стойност:**
- Изчакай още 30-60 минути
- DNS може да отнеме до 48 часа за пълно разпространение

### Стъпка 4: Проверка в Railway

1. Отиди на Railway → Settings → Domains
2. Намери `www.marbaras.com`
3. Провери дали е "Active" (зелена отметка)
4. Ако не е, кликни "Check DNS"

### Стъпка 5: Тествай в браузъра

1. Отиди на `https://www.marbaras.com`
2. Ако все още виждаш 404:
   - Провери Railway logs за грешки
   - Убеди се че Variables са правилно настроени
   - Изчакай още малко за DNS да се разпространи

---

## Проверка на Railway Logs:

1. Отиди на Railway → **Logs** tab
2. Провери за грешки като:
   - "DisallowedHost"
   - "404"
   - "Invalid host header"

**Ако виждаш "DisallowedHost":**
- Убеди се че `DJANGO_ALLOWED_HOSTS` включва `www.marbaras.com`

---

## Алтернативна проверка:

Ако все още има проблеми, провери дали Railway домейнът работи:

1. Отиди на `https://marbaras-production.up.railway.app`
2. Ако този домейн работи, проблемът е с custom domain
3. Ако и този не работи, проблемът е с приложението

---

## Важно:

- След промяна на Variables, Railway автоматично redeploy-ва
- Изчакай 2-3 минути след промяна на Variables
- DNS може да отнеме време за разпространение
- Убеди се че всички Variables са правилно настроени

---

## Ако все още има проблеми:

1. Провери Railway logs за конкретни грешки
2. Убеди се че всички Variables са правилно настроени
3. Провери DNS разпространение с DNS Checker
4. Сподели:
   - Какво показват Railway logs
   - Какви Variables имаш в Railway
   - Какво показва DNS Checker

