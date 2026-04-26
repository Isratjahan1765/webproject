"""
Management command to seed the database with sample data.
Usage: python manage.py seed_data
"""

import random
from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from products.models import Product, ProductCategory, ProductUnit
from drivers.models import Driver, VehicleType
from arrivals.models import Arrival, ArrivalItem, ArrivalStatus, QualityGrade
from pickups.models import Pickup, PickupItem, PickupStatus
from inventory.services import InventoryService
from arrivals.services import ArrivalService
from pickups.services import PickupService
from accounts.models import Profile, UserRole


class Command(BaseCommand):
    help = 'Seed the database with sample data for SPHWMS'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding SPHWMS database...\n')

        # Create manager user
        manager, created = User.objects.get_or_create(
            username='manager',
            defaults={
                'first_name': 'Warehouse',
                'last_name': 'Manager',
                'email': 'manager@sphwms.local',
                'is_staff': True,
            }
        )
        if created:
            manager.set_password('manager123')
            manager.save()
            Profile.objects.filter(user=manager).update(
                role=UserRole.MANAGER,
                phone='01712345678',
                designation='Senior Warehouse Manager',
            )
            self.stdout.write(self.style.SUCCESS('✓ Manager user created (manager/manager123)'))

        # Create products
        products_data = [
            {'name': 'Miniket Rice', 'name_bn': 'মিনিকেট চাল', 'sku': 'RIC-00001', 'category': 'rice', 'unit': 'kg', 'unit_price': Decimal('65.00'), 'minimum_stock': Decimal('500')},
            {'name': 'Nazirshail Rice', 'name_bn': 'নাজিরশাইল চাল', 'sku': 'RIC-00002', 'category': 'rice', 'unit': 'kg', 'unit_price': Decimal('72.00'), 'minimum_stock': Decimal('300')},
            {'name': 'BR-28 Wheat', 'name_bn': 'বিআর-২৮ গম', 'sku': 'WHE-00001', 'category': 'wheat', 'unit': 'kg', 'unit_price': Decimal('42.00'), 'minimum_stock': Decimal('400')},
            {'name': 'Red Lentil (Masoor)', 'name_bn': 'মসুর ডাল', 'sku': 'PUL-00001', 'category': 'pulse', 'unit': 'kg', 'unit_price': Decimal('120.00'), 'minimum_stock': Decimal('200')},
            {'name': 'Mustard Seeds', 'name_bn': 'সরিষা', 'sku': 'OIL-00001', 'category': 'oilseed', 'unit': 'kg', 'unit_price': Decimal('95.00'), 'minimum_stock': Decimal('150')},
            {'name': 'Turmeric Powder', 'name_bn': 'হলুদ গুঁড়া', 'sku': 'SPI-00001', 'category': 'spice', 'unit': 'kg', 'unit_price': Decimal('280.00'), 'minimum_stock': Decimal('100')},
            {'name': 'Red Chilli Powder', 'name_bn': 'মরিচ গুঁড়া', 'sku': 'SPI-00002', 'category': 'spice', 'unit': 'kg', 'unit_price': Decimal('350.00'), 'minimum_stock': Decimal('80')},
            {'name': 'Potato (Diamond)', 'name_bn': 'আলু (ডায়মন্ড)', 'sku': 'VEG-00001', 'category': 'vegetable', 'unit': 'kg', 'unit_price': Decimal('30.00'), 'minimum_stock': Decimal('1000')},
            {'name': 'Onion (Local)', 'name_bn': 'পেঁয়াজ (দেশি)', 'sku': 'VEG-00002', 'category': 'vegetable', 'unit': 'kg', 'unit_price': Decimal('55.00'), 'minimum_stock': Decimal('800')},
            {'name': 'Urea Fertilizer', 'name_bn': 'ইউরিয়া সার', 'sku': 'FER-00001', 'category': 'fertilizer', 'unit': 'bag', 'unit_price': Decimal('900.00'), 'minimum_stock': Decimal('50')},
            {'name': 'BARI Mango', 'name_bn': 'বারি আম', 'sku': 'FRU-00001', 'category': 'fruit', 'unit': 'kg', 'unit_price': Decimal('150.00'), 'minimum_stock': Decimal('200')},
            {'name': 'Paddy (BRRI-29)', 'name_bn': 'ধান (ব্রি-২৯)', 'sku': 'GRA-00001', 'category': 'grain', 'unit': 'kg', 'unit_price': Decimal('28.00'), 'minimum_stock': Decimal('1000')},
        ]

        products = []
        for pd in products_data:
            product, created = Product.objects.get_or_create(sku=pd['sku'], defaults=pd)
            products.append(product)
            if created:
                self.stdout.write(f'  ✓ Product: {product.name}')

        # Create drivers
        drivers_data = [
            {'name': 'Rahim Uddin', 'phone': '01811111111', 'license_number': 'DL-2024-001', 'vehicle_type': 'truck', 'vehicle_number': 'DHA-12-3456'},
            {'name': 'Karim Sheikh', 'phone': '01822222222', 'license_number': 'DL-2024-002', 'vehicle_type': 'lorry', 'vehicle_number': 'DHA-34-5678'},
            {'name': 'Jamal Hossain', 'phone': '01833333333', 'license_number': 'DL-2024-003', 'vehicle_type': 'pickup', 'vehicle_number': 'CTG-11-2233'},
            {'name': 'Faruk Ahmed', 'phone': '01844444444', 'license_number': 'DL-2024-004', 'vehicle_type': 'truck', 'vehicle_number': 'RAJ-22-4455'},
            {'name': 'Salam Mia', 'phone': '01855555555', 'license_number': 'DL-2024-005', 'vehicle_type': 'van', 'vehicle_number': 'KHU-33-6677'},
        ]

        drivers = []
        for dd in drivers_data:
            driver, created = Driver.objects.get_or_create(phone=dd['phone'], defaults=dd)
            drivers.append(driver)
            if created:
                self.stdout.write(f'  ✓ Driver: {driver.name}')

        # Create arrivals with items
        now = timezone.now()
        for i in range(6):
            arrival_date = now - timedelta(days=random.randint(1, 60))
            arrival = Arrival.objects.create(
                driver=random.choice(drivers),
                arrival_date=arrival_date,
                source_location=random.choice(['Bogra', 'Rangpur', 'Dinajpur', 'Rajshahi', 'Mymensingh']),
                status=ArrivalStatus.PENDING,
            )
            # Add 2-4 items
            selected_products = random.sample(products, min(random.randint(2, 4), len(products)))
            for product in selected_products:
                qty = Decimal(str(random.randint(50, 500)))
                ArrivalItem.objects.create(
                    arrival=arrival,
                    product=product,
                    quantity=qty,
                    unit_price_at_arrival=product.unit_price,
                    quality_grade=random.choice([QualityGrade.A, QualityGrade.B, QualityGrade.A]),
                )
            self.stdout.write(f'  ✓ Arrival: {arrival.batch_number} ({arrival.total_items} items)')

        # Confirm some arrivals (which adds to inventory)
        pending_arrivals = Arrival.objects.filter(status=ArrivalStatus.PENDING)[:4]
        for arrival in pending_arrivals:
            try:
                ArrivalService.confirm_arrival(arrival.pk, manager)
                self.stdout.write(f'  ✓ Confirmed: {arrival.batch_number}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ! Could not confirm {arrival.batch_number}: {e}'))

        # Create pickups
        for i in range(4):
            pickup_date = now - timedelta(days=random.randint(1, 30))
            pickup = Pickup.objects.create(
                driver=random.choice(drivers),
                pickup_date=pickup_date,
                destination=random.choice(['Dhaka Market', 'Chittagong Port', 'Sylhet Depot', 'Khulna Center']),
                buyer_name=random.choice(['ABC Trading', 'XYZ Exports', 'Local Market', 'Farm Fresh Ltd']),
                buyer_phone='018' + str(random.randint(10000000, 99999999)),
                status=PickupStatus.PENDING,
            )
            selected = random.sample(products, min(random.randint(1, 3), len(products)))
            for product in selected:
                qty = Decimal(str(random.randint(10, 100)))
                PickupItem.objects.create(
                    pickup=pickup,
                    product=product,
                    quantity=qty,
                    unit_price_at_pickup=product.unit_price,
                )
            self.stdout.write(f'  ✓ Pickup: {pickup.pickup_number} → {pickup.destination}')

        # Confirm some pickups
        pending_pickups = Pickup.objects.filter(status=PickupStatus.PENDING)[:2]
        for pickup in pending_pickups:
            try:
                PickupService.confirm_pickup(pickup.pk, manager)
                self.stdout.write(f'  ✓ Confirmed pickup: {pickup.pickup_number}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ! Could not confirm pickup: {e}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('   Login: manager / manager123'))
        self.stdout.write(self.style.SUCCESS('   URL:   http://127.0.0.1:8000/'))
