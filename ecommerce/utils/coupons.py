import secrets
import string
from ecommerce.models import Coupon

ALPHABET = string.ascii_uppercase + string.digits

def generate_code(prefix: str = "", length: int = 8) -> str:
    base = "".join(secrets.choice(ALPHABET) for _ in range(length))
    return f"{prefix}{base}"

def create_batch(count: int, *, prefix="", percent_off=None, amount_off=None,
                 starts_at=None, ends_at=None, usage_limit=None, active=True):
    created = []
    for _ in range(count):
        code = generate_code(prefix=prefix)
        while Coupon.objects.filter(code=code).exists():
            code = generate_code(prefix=prefix)
        created.append(Coupon(
            code=code,
            percent_off=percent_off,
            amount_off=amount_off,
            starts_at=starts_at,
            ends_at=ends_at,
            usage_limit=usage_limit,
            active=active,
        ))
    Coupon.objects.bulk_create(created)
    return [c.code for c in created]
