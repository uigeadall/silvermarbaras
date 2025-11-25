# 📸 Качи Media Файловете в Railway

## Проблем
Снимките на продуктите не се показват, защото media файловете (324MB, 1163 файла) не са качени в Railway.

## Решение: Използвай Railway Volume

### Стъпка 1: Създай Volume в Railway

1. Отиди на Railway Dashboard: https://railway.app/dashboard
2. Избери проект: **hearty-optimism**
3. Избери service: **marbaras**
4. Отиди на таба **"Settings"**
5. Скролни до секцията **"Volumes"**
6. Кликни **"+ New Volume"**
7. Име: `media-volume`
8. Mount Path: `/app/media`
9. Кликни **"Create"**

### Стъпка 2: Качи Media Файловете

#### Опция A: Използвай Railway CLI (Ако работи)

```bash
cd /Users/antonkondachiev/Desktop/МагазинСребро

# Свържи се към Railway
railway link

# Качи media файловете
railway run rsync -avz media/ /app/media/
```

#### Опция B: Използвай Railway Dashboard Shell

1. В Railway Dashboard → `marbaras` service
2. Търси опция **"Shell"** или **"Console"**
3. Ако намериш, изпълни:
   ```bash
   # Създай директорията
   mkdir -p /app/media/products
   
   # Качи файловете (ще трябва да ги качиш ръчно или чрез друг метод)
   ```

#### Опция C: Използвай Cloud Storage (Препоръчително)

Най-доброто решение е да използваш cloud storage (AWS S3, Cloudinary, etc.) за media файловете.

**Предимства:**
- По-бързо зареждане
- По-добра производителност
- Автоматично backup
- По-евтино от Railway Volume

**Опции:**
1. **Cloudinary** (безплатно до 25GB): https://cloudinary.com
2. **AWS S3** (pay-as-you-go)
3. **Railway Volume** (просто, но по-скъпо)

---

## Алтернатива: Качи Media Файловете в Git (Не Препоръчително)

Ако media файловете не са твърде големи, можеш да ги качиш в git:

1. Премахни `/media` от `.gitignore`
2. Качи media файловете в git:
   ```bash
   git add media/
   git commit -m "Add media files"
   git push
   ```
3. Railway автоматично ще ги качи при следващия deploy

**Внимание:** Това не е препоръчително за големи файлове (324MB е доста голямо за git).

---

## Проверка след качване

1. Отиди на приложението: https://marbaras-production.up.railway.app
2. Провери дали снимките се показват
3. Отвори developer tools (F12) → Network tab
4. Провери дали снимките се зареждат от `/media/products/`

---

## Следващи стъпки

Сподели:
1. Имаш ли опция за Volume в Railway Dashboard?
2. Имаш ли опция за Shell в Railway Dashboard?
3. Предпочиташ ли cloud storage или Railway Volume?

