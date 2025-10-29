from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Sanity check command discovery"

    def handle(self, *args, **opts):
        self.stdout.write(self.style.SUCCESS("✅ hello command loaded"))
