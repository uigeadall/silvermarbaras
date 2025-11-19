# 🔧 Отстраняване на Проблеми с Railway Volume

## Проблем: Volume е създаден, но не се монтира

Ако Volume е създаден в Railway Dashboard, но скриптът все още казва че не е монтиран, следвай тези стъпки:

## Стъпка 1: Проверка в Railway Dashboard

### 1.1. Провери дали Volume е свързан към service-а

1. Отиди на Railway Dashboard: https://railway.app/dashboard
2. Избери проект: **hearty-optimism**
3. Избери service: **marbaras**
4. Отиди на таба **"Architecture"** (или "Settings")
5. Провери дали виждаш Volume `marbaras-volume` свързан към service `marbaras`

### 1.2. Провери Mount Path

1. В Railway Dashboard → service `marbaras`
2. Settings → Volumes
3. Кликни на `marbaras-volume`
4. Провери **Mount Path** - трябва да е точно `/app/media` (без кавички, без интервали)

### 1.3. Провери дали Volume е активен

В Settings → Volumes, Volume-ът трябва да има:
- ✅ Зелен статус
- ✅ Mount Path: `/app/media`
- ✅ Размер (например 500 MB)

## Стъпка 2: Направи Redeploy

**ВАЖНО**: След като създадеш или промениш Volume, **ЗАДЪЛЖИТЕЛНО** трябва да направиш redeploy!

### Опция A: Redeploy от Dashboard

1. В Railway Dashboard → service `marbaras`
2. Кликни на таба **"Deployments"**
3. Намери последния deployment
4. Кликни на трите точки (⋮) → **"Redeploy"**

ИЛИ

1. В Railway Dashboard → service `marbaras`
2. Кликни на бутона **"Redeploy"** (ако го виждаш)

### Опция B: Redeploy чрез GitHub

Ако имаш GitHub integration:

```bash
git commit --allow-empty -m "Redeploy for Volume mount"
git push github newone
```

### Опция C: Redeploy чрез Railway CLI

```bash
railway up --detach
```

## Стъпка 3: Проверка след Redeploy

След като redeploy приключи (обикновено 2-3 минути):

### 3.1. Провери Railway Logs

1. В Railway Dashboard → service `marbaras`
2. Отиди на таба **"Logs"**
3. Търси за съобщения за Volume mount
4. Провери дали има грешки

### 3.2. Провери чрез CLI

```bash
railway run bash -c "ls -la /app 2>&1"
```

Трябва да видиш `/app/media` директорията.

### 3.3. Провери чрез скрипта

```bash
./scripts/upload_media_to_railway.sh
```

Сега трябва да каже че Volume е монтиран.

## Стъпка 4: Ако все още не работи

### 4.1. Изтрий и създай Volume отново

1. В Railway Dashboard → service `marbaras`
2. Settings → Volumes
3. Кликни на `marbaras-volume`
4. Кликни **"Delete"** или **"Remove"**
5. Създай Volume отново:
   - Name: `marbaras-volume`
   - Mount Path: `/app/media`
6. **Redeploy service-а**

### 4.2. Провери дали service-ът е правилният

Увери се че Volume е свързан към правилния service:
- Service name: `marbaras` (не `MySQL` или друг)
- Environment: `production` (или правилният environment)

### 4.3. Провери Railway Documentation

Railway понякога променя как работи Volume mounting. Провери:
- https://docs.railway.app/storage/volumes

## Често Срещани Грешки

### Грешка 1: "No such file or directory: /app"

**Причина**: Volume не е монтиран или не е направен redeploy.

**Решение**: Направи redeploy на service-а.

### Грешка 2: "Read-only file system"

**Причина**: Volume не е монтиран правилно или Mount Path е грешен.

**Решение**: 
1. Провери Mount Path да е точно `/app/media`
2. Направи redeploy

### Грешка 3: Volume съществува, но файловете не се запазват

**Причина**: `MEDIA_ROOT` в settings.py не сочи към Volume.

**Решение**: Провери `МагазинСребро/settings.py` - `MEDIA_ROOT` трябва да е `/app/media`.

## Следващи Стъпки

След като Volume е монтиран правилно:

1. ✅ Изпълни `./scripts/upload_media_to_railway.sh`
2. ✅ Провери дали файловете са качени
3. ✅ Тествай дали снимките се показват в приложението
4. ✅ Направи redeploy и провери дали файловете се запазват

