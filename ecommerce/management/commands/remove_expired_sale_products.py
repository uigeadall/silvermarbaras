"""
Management command to remove products from Sale category when sale_expires_at time has passed.
Run this command periodically (e.g., via cron) to automatically clean up expired sale products.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from ecommerce.models import Product, Category


class Command(BaseCommand):
    help = 'Remove products from Sale category when sale_expires_at time has expired'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be removed without actually removing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        
        # Get Sale category
        try:
            sale_category = Category.objects.filter(
                name__iexact='Sale'
            ).first()
            
            if not sale_category:
                # Try Bulgarian name
                sale_category = Category.objects.filter(
                    name__icontains='разпродажба'
                ).first()
            
            if not sale_category:
                self.stdout.write(
                    self.style.WARNING('Sale category not found. Skipping.')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error finding Sale category: {e}')
            )
            return
        
        # Find products in Sale category with expired sale_expires_at
        expired_products = Product.objects.filter(
            categories=sale_category,
            sale_expires_at__isnull=False,
            sale_expires_at__lt=now
        ).distinct()
        
        count = expired_products.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No expired sale products found.')
            )
            return
        
        self.stdout.write(
            f'Found {count} product(s) with expired sale time:'
        )
        
        for product in expired_products:
            self.stdout.write(
                f'  - {product.name} (ID: {product.id}, expired at: {product.sale_expires_at})'
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\nDRY RUN: No changes made. Remove --dry-run to actually remove products from Sale.'
                )
            )
            return
        
        # Remove products from Sale category
        removed_count = 0
        with transaction.atomic():
            for product in expired_products:
                product.categories.remove(sale_category)
                removed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Removed "{product.name}" from Sale category'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully removed {removed_count} product(s) from Sale category.'
            )
        )

