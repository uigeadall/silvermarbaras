# ecommerce/management/commands/test_emails.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from ecommerce.models import Order, OrderItem, Product, ShippingOption
from ecommerce.utils.emailing import (
    send_welcome_email,
    send_order_confirmation_email,
    send_order_shipped_email,
    send_password_reset_email,
)
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test email sending functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test emails to',
            required=True,
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['welcome', 'order', 'shipped', 'reset', 'all'],
            default='all',
            help='Type of email to test',
        )

    def handle(self, *args, **options):
        email = options['email']
        email_type = options['type']
        base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')

        self.stdout.write(self.style.SUCCESS(f'\n📧 Тестване на имейли до: {email}'))
        self.stdout.write(self.style.SUCCESS(f'🌐 Base URL: {base_url}\n'))

        # Test Welcome Email
        if email_type in ['welcome', 'all']:
            self.stdout.write(self.style.WARNING('Тестване на Welcome Email...'))
            try:
                # Create or get a test user
                user, created = User.objects.get_or_create(
                    username='test_user',
                    defaults={'email': email, 'first_name': 'Тест', 'last_name': 'Потребител'}
                )
                if not created:
                    user.email = email
                    user.save()

                if send_welcome_email(user, base_url):
                    self.stdout.write(self.style.SUCCESS('✅ Welcome email изпратен успешно!\n'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Грешка при изпращане на Welcome email\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Грешка: {e}\n'))

        # Test Order Confirmation Email
        if email_type in ['order', 'all']:
            self.stdout.write(self.style.WARNING('Тестване на Order Confirmation Email...'))
            try:
                # Get or create a test user
                user, _ = User.objects.get_or_create(
                    username='test_user',
                    defaults={'email': email}
                )
                if user.email != email:
                    user.email = email
                    user.save()

                # Get or create a shipping option
                shipping, _ = ShippingOption.objects.get_or_create(
                    name='Standard',
                    defaults={'price': Decimal('5.00'), 'delivery_time': '3-5 дни'}
                )

                # Get a product (or create a dummy one)
                product = Product.objects.first()
                if not product:
                    self.stdout.write(self.style.ERROR('❌ Няма продукти в базата данни. Създайте поне един продукт.\n'))
                    return

                # Create a test order
                order = Order.objects.create(
                    user=user,
                    email=email,
                    full_name='Тест Потребител',
                    address='Тестова Адрес 123',
                    city='София',
                    postal_code='1000',
                    phone='+359888123456',
                    shipping_option=shipping,
                    total_price=Decimal('99.99'),
                )

                # Create order items
                variant = product.variants.first()
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variant,
                    quantity=2,
                )

                if send_order_confirmation_email(order, base_url, notify_admin=False):
                    self.stdout.write(self.style.SUCCESS('✅ Order confirmation email изпратен успешно!\n'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Грешка при изпращане на Order confirmation email\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Грешка: {e}\n'))

        # Test Order Shipped Email
        if email_type in ['shipped', 'all']:
            self.stdout.write(self.style.WARNING('Тестване на Order Shipped Email...'))
            try:
                # Get the test order or create a new one
                order = Order.objects.filter(email=email).first()
                if not order:
                    user, _ = User.objects.get_or_create(
                        username='test_user',
                        defaults={'email': email}
                    )
                    shipping, _ = ShippingOption.objects.get_or_create(
                        name='Standard',
                        defaults={'price': Decimal('5.00'), 'delivery_time': '3-5 дни'}
                    )
                    product = Product.objects.first()
                    if not product:
                        self.stdout.write(self.style.ERROR('❌ Няма продукти в базата данни.\n'))
                        return

                    order = Order.objects.create(
                        user=user,
                        email=email,
                        full_name='Тест Потребител',
                        address='Тестова Адрес 123',
                        city='София',
                        postal_code='1000',
                        phone='+359888123456',
                        shipping_option=shipping,
                        total_price=Decimal('99.99'),
                    )
                    variant = product.variants.first()
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        variant=variant,
                        quantity=1,
                    )

                if send_order_shipped_email(order, base_url, tracking_number='TEST123456'):
                    self.stdout.write(self.style.SUCCESS('✅ Order shipped email изпратен успешно!\n'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Грешка при изпращане на Order shipped email\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Грешка: {e}\n'))

        # Test Password Reset Email
        if email_type in ['reset', 'all']:
            self.stdout.write(self.style.WARNING('Тестване на Password Reset Email...'))
            try:
                user, _ = User.objects.get_or_create(
                    username='test_user',
                    defaults={'email': email}
                )
                if user.email != email:
                    user.email = email
                    user.save()

                reset_url = f"{base_url}/accounts/password/reset/?token=test_token_12345"
                if send_password_reset_email(user, reset_url, base_url):
                    self.stdout.write(self.style.SUCCESS('✅ Password reset email изпратен успешно!\n'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Грешка при изпращане на Password reset email\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Грешка: {e}\n'))

        self.stdout.write(self.style.SUCCESS('\n✨ Тестването приключи!\n'))
        self.stdout.write(self.style.WARNING('💡 Съвет: Проверете вашия email inbox (и spam папката).\n'))

