#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import ConstantTable

# Create ConstantTable record for +1 country code
constant_table, created = ConstantTable.objects.get_or_create(
    country_code='+1',
    defaults={
        'allow_registration': True,
        'allow_vehicle_registration': True,
        'base_rate': 5.0,
        'economy_kilometer_rate': 2.5,
        'suv_kilometer_rate': 3.5,
        'luxury_kilometer_rate': 4.0,
        'time_based_rate': 0.5,
        'peak_hour_rate': 1.5,
        'package_delivery_rate': 1.0,
    }
)

if created:
    print("✅ Created ConstantTable record for country code +1")
else:
    print("✅ ConstantTable record for country code +1 already exists")

print(f"Country Code: {constant_table.country_code}")
print(f"Allow Registration: {constant_table.allow_registration}")
print(f"Allow Vehicle Registration: {constant_table.allow_vehicle_registration}")
