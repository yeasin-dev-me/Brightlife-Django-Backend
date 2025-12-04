import os

from django.core.exceptions import ValidationError
from PIL import Image


def validate_file_size(file, max_size_mb=5):
    """Validate file size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(f"File size cannot exceed {max_size_mb}MB")


def validate_image_dimensions(image, max_width=2000, max_height=2000):
    """Validate image dimensions"""
    img = Image.open(image)
    if img.width > max_width or img.height > max_height:
        raise ValidationError(
            f"Image dimensions cannot exceed {max_width}x{max_height}px"
        )


def get_file_extension(filename):
    """Get file extension safely"""
    return os.path.splitext(filename)[1].lower()
