"""
Script to create a Django superuser non-interactively during deployment.
Reads credentials from environment variables:
  - DJANGO_SUPERUSER_USERNAME  (default: admin)
  - DJANGO_SUPERUSER_EMAIL     (default: admin@example.com)
  - DJANGO_SUPERUSER_PASSWORD  (required – set this in Render's env vars)
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital_portal.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402 – must come after setup()

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")

if not password:
    print(
        "WARNING: DJANGO_SUPERUSER_PASSWORD is not set. "
        "Skipping superuser creation."
    )
else:
    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists – skipping creation.")
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully.")
