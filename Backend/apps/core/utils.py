import os
import uuid
from django.utils.text import slugify


def upload_to_path(instance, filename):
    """
    Generate upload path for files
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(
        instance.__class__.__name__.lower(),
        str(instance.id),
        filename
    )


def generate_unique_slug(model_class, title, slug_field='slug'):
    """
    Generate a unique slug for a model instance
    """
    base_slug = slugify(title)
    slug = base_slug
    counter = 1

    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def format_currency(amount, currency='USD'):
    """
    Format currency amount
    """
    if currency == 'USD':
        return f"${amount:.2f}"
    return f"{amount:.2f} {currency}"