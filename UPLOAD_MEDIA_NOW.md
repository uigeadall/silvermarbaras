# 🚀 Качи Media Файловете СЕГА

## Проблем
Старите снимки не се показват, защото са били в ефемерната файлова система и са се изтрили при redeploy.

## Решение: Качи Файловете в Railway Volume

### Предпоставки
1. ✅ Railway Volume е създаден (`marbaras-volume` на `/app/media`)
2. ✅ Railway CLI е инсталиран

### Стъпка 1: Инсталирай Railway CLI (ако нямаш)

```bash
npm i -g @railway/cli
```

### Стъпка 2: Login и Link

```bash
# Login в Railway
railway login

# Link към проекта
cd /Users/antonkondachiev/Desktop/МагазинСребро
railway link
# Избери проекта и service-а
```

### Стъпка 3: Качи Файловете

#### Опция A: Използвай Скрипта (Най-лесно)

```bash
cd /Users/antonkondachiev/Desktop/МагазинСребро
./scripts/upload_media_to_railway.sh
```

#### Опция B: Ръчно с Railway CLI

```bash
# Създай директориите
railway run bash -c "mkdir -p /app/media/products /app/media/products/multiple"

# Качи файловете (използвай tar за по-бързо качване)
cd media
tar -czf - products/ | railway run bash -c "cd /app/media && tar -xzf -"
cd ..
```

#### Опция C: Качи чрез Admin Panel (Бавно, но работи)

1. Отиди на Django Admin
2. За всеки продукт качи снимките отново
3. Те ще се запазят в Volume

### Стъпка 4: Проверка

1. Провери в Railway Dashboard → Deployments → последния deployment → Logs
2. Търси съобщения за качени файлове
3. Отиди на приложението и провери дали снимките се показват
4. Направи redeploy и провери дали снимките все още се показват

## Важно

- **Файловете в Volume се запазват между redeploy**
- **Новите файлове, качени след това, ще се запазват автоматично**
- **Не е нужно да качваш файловете отново при всеки redeploy**

## Ако Скриптът Не Работи

Използвай опция C (Admin Panel) - бавно е, но работи винаги.

