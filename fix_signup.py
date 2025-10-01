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

print(f"✅ ConstantTable for +1: {'Created' if created else 'Already exists'}")
print(f"Allow Registration: {constant_table.allow_registration}")
print(f"Allow Vehicle Registration: {constant_table.allow_vehicle_registration}")

# Test the signup serializer validation
from core.serializer import RegistrationSerializer

test_data = {
    "email": "test@example.com",
    "password": "Test123!",
    "confirm_password": "Test123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567891",
    "country_code": "+1",
    "user_type": "USER"
}

serializer = RegistrationSerializer(data=test_data)
if serializer.is_valid():
    print("✅ Serializer validation passed")
else:
    print("❌ Serializer validation failed:")
    print(serializer.errors)
