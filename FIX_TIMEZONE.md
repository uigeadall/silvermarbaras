# Fix MySQL Timezone Issues

## Проблем

Django Admin `date_hierarchy` изисква timezone support в MySQL, но по подразбиране MySQL няма инсталирани timezone таблици.

## Решение 1: Премахване на date_hierarchy (Временно - вече направено)

Временно премахнах `date_hierarchy` от `OrderAdmin`. Това решава проблема, но губиш удобството за филтриране по дати в admin.

## Решение 2: Инсталиране на Timezone таблици в MySQL (Препоръчано)

### Стъпка 1: Намери timezone файлове

```bash
# На macOS с Homebrew MySQL
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql

# На Linux
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql

# Или ако имаш mysql_tzinfo_to_sql в друг път
which mysql_tzinfo_to_sql
```

### Стъпка 2: Инсталирай timezone таблици

```bash
mysql -u root -p mysql < /path/to/timezone_tables.sql
```

Или директно:

```bash
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql
```

### Стъпка 3: Провери

```sql
mysql -u root -p
USE mysql;
SHOW TABLES LIKE '%time%';
-- Трябва да видиш: time_zone, time_zone_leap_second, time_zone_name, time_zone_transition, time_zone_transition_type
```

### Стъпка 4: Включи отново date_hierarchy

В `ecommerce/admin.py`:
```python
date_hierarchy = "created_at"  # Сега ще работи!
```

## Решение 3: Използване на USE_TZ = False (НЕ препоръчано)

Това ще реши проблема, но не е добра практика за production. Django препоръчва `USE_TZ = True`.

## Решение 4: Кастомна date_hierarchy (Алтернатива)

Можеш да създадеш кастомен date hierarchy без timezone конверсии:

```python
# В admin.py
def get_queryset(self, request):
    qs = super().get_queryset(request)
    # Използвай naive datetime за date_hierarchy
    return qs
```

## Проверка

След инсталиране на timezone таблици, провери:

```python
python3 manage.py shell
>>> from django.db import connection
>>> cursor = connection.cursor()
>>> cursor.execute("SELECT @@global.time_zone, @@session.time_zone")
>>> print(cursor.fetchall())
```

## Текущо състояние

Временно премахнах `date_hierarchy` за да работи admin. За да го върнеш:

1. Инсталирай timezone таблици в MySQL (Решение 2)
2. Включи отново `date_hierarchy = "created_at"` в `ecommerce/admin.py`

