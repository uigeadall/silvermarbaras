# Проверка и поправка на Railway деплоймента

## Проблем
Промените са push-нати в GitHub, но Railway не деплойва автоматично.

## Стъпки за проверка и поправка

### 1. Проверка на Railway Dashboard

1. Отвори Railway Dashboard: https://railway.app
2. Избери проекта
3. Отиди на **Settings** → **Service** → **Source**
4. Провери:
   - **Repository**: Трябва да е `uigeadall/marbaras123` или правилният repo
   - **Branch**: Трябва да е `newone` (не `main` или `master`)
   - **Auto Deploy**: Трябва да е **enabled**

### 2. Ако Branch не е `newone`

1. В Railway Dashboard → **Settings** → **Service** → **Source**
2. Промени **Branch** от `main`/`master` на `newone`
3. Кликни **Save**
4. Railway автоматично ще започне нов деплоймент

### 3. Ако Auto Deploy е disabled

1. В Railway Dashboard → **Settings** → **Service** → **Source**
2. Включи **Auto Deploy**
3. Кликни **Save**

### 4. Manual Deploy (ако auto-deploy не работи)

1. В Railway Dashboard → **Deployments**
2. Кликни **Deploy** или **Redeploy**
3. Избери **Deploy from GitHub**
4. Избери `newone` branch
5. Кликни **Deploy**

### 5. Проверка на GitHub Connection

1. В Railway Dashboard → **Settings** → **Service** → **Source**
2. Провери дали GitHub connection е активен
3. Ако не е, кликни **Connect GitHub** и следвай инструкциите

### 6. Проверка на Deployments Logs

1. В Railway Dashboard → **Deployments**
2. Отвори последния deployment
3. Провери logs за грешки
4. Ако има грешки, копирай ги и ги сподели

### 7. Проверка на Environment Variables

1. В Railway Dashboard → **Variables**
2. Провери дали всички необходими променливи са зададени:
   - `DJANGO_SECRET_KEY`
   - `DATABASE_URL`
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `DJANGO_ALLOWED_HOSTS`
   - и др.

### 8. Ако нищо не работи - Force Redeploy

1. В Railway Dashboard → **Deployments**
2. Намери последния успешен deployment
3. Кликни **Redeploy**
4. Или изтрий service и създай нов с правилния branch

## Бързо решение

Ако искаш бързо да деплойнеш промените:

1. Отвори Railway Dashboard
2. Отиди на **Settings** → **Service** → **Source**
3. Промени **Branch** на `newone`
4. Включи **Auto Deploy** (ако не е включен)
5. Кликни **Save**
6. Railway автоматично ще започне деплоймент

## Проверка след деплой

След като деплойментът приключи:

1. Отвори сайта: https://www.marbaras.com
2. Провери дали промените са налице:
   - Mobile menu на login страницата трябва да има съдържание
   - Currency conversion трябва да работи на product detail страницата
   - Изображенията трябва да се зареждат по-бързо

## Ако проблемът продължава

1. Провери Railway logs за грешки
2. Провери дали GitHub repo е правилният
3. Провери дали има проблеми с Railway service
4. Свържи се с Railway support ако е необходимо

