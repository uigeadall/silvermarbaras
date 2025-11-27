from django.core.management.base import BaseCommand
from django.utils import timezone
from ecommerce.utils.coupons import create_batch

class Command(BaseCommand):
    help = "Generate a batch of promo codes"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=50)
        parser.add_argument("--prefix", type=str, default="PROMO-")
        parser.add_argument("--percent", type=float, default=None)
        parser.add_argument("--amount", type=float, default=None)
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument("--usage", type=int, default=1)

    def handle(self, *args, **opts):
        now = timezone.now()
        starts_at = now
        ends_at = now + timezone.timedelta(days=opts["days"])

        codes = create_batch(
            opts["count"],
            prefix=opts["prefix"],
            percent_off=opts["percent"],
            amount_off=opts["amount"],
            starts_at=starts_at,
            ends_at=ends_at,
            usage_limit=opts["usage"],
            active=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Generated {len(codes)} coupons"))
        for c in codes:
            self.stdout.write(c)
