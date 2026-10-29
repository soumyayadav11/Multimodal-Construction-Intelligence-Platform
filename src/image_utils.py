"""Image processing utilities for the Construction Intelligence Platform."""
from __future__ import annotations

import io
from typing import Any
from PIL import Image

try:
    from src.config import AppConfig
except ImportError:
    # Fallback configuration if src.config is not yet initialized
    class AppConfig:  # type: ignore[no-redef]
        """Fallback configuration for image processing utilities."""
        SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        MAX_FILE_SIZE_MB = 10


def validate_image_file(uploaded_file: Any) -> tuple[bool, str]:
    """Validate uploaded image file type and size.
    
    Args:
        uploaded_file: Streamlit UploadedFile object or file-like object with type and size attributes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "No file uploaded."
    
    # Check file type against supported types (handles both MIME types like 'image/png' and extensions like 'png')
    file_type = getattr(uploaded_file, "type", "").lower()
    file_name = getattr(uploaded_file, "name", "").lower()
    ext = file_name.rsplit(".", 1)[-1] if "." in file_name else ""
    
    supported_raw = set(getattr(AppConfig, "SUPPORTED_IMAGE_TYPES", ["image/jpeg", "image/png", "image/jpg"]))
    supported_normalized = {str(t).lower().replace("image/", "") for t in supported_raw}
    
    is_supported = (
        file_type in supported_raw
        or file_type.replace("image/", "") in supported_normalized
        or ext in supported_normalized
    )
    if not is_supported:
        return False, f"Unsupported file type: {file_type or ext}. Please upload JPG, JPEG, or PNG."
    
    # Check file size
    file_size = getattr(uploaded_file, "size", 0)
    file_size_mb = file_size / (1024 * 1024)
    if file_size_mb > AppConfig.MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f} MB) exceeds the {AppConfig.MAX_FILE_SIZE_MB} MB limit."
    
    return True, ""


def load_image(uploaded_file: Any) -> Image.Image | None:
    """Load and return a PIL Image from an uploaded file.
    
    Args:
        uploaded_file: File-like object or path containing image data
        
    Returns:
        PIL Image instance, or None if image loading/verification fails
    """
    try:
        image = Image.open(uploaded_file)
        image.verify()  # Verify it's a valid image
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)  # Reset file pointer after verify
        image = Image.open(uploaded_file)  # Re-open after verify
        image.load()  # Ensure image data is loaded into memory
        return image
    except Exception:
        return None


def resize_image_for_api(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """Resize image if needed for API submission while maintaining aspect ratio.
    
    Args:
        image: Original PIL Image
        max_size: Maximum dimension (width or height) in pixels
        
    Returns:
        Resized PIL Image or original if within max dimensions
    """
    width, height = image.size
    if width <= max_size and height <= max_size:
        return image
    
    ratio = min(max_size / width, max_size / height)
    new_size = (max(1, int(width * ratio)), max(1, int(height * ratio)))
    
    # Handle Pillow 9/10/11 resampling filter deprecation gracefully
    resample_filter = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)
    return image.resize(new_size, resample_filter)


def image_to_bytes(image: Image.Image, format: str = "JPEG") -> bytes:
    """Convert PIL Image to bytes.
    
    Args:
        image: PIL Image instance
        format: Target format (e.g., 'JPEG', 'PNG')
        
    Returns:
        Raw image bytes
    """
    buffer = io.BytesIO()
    fmt_upper = format.upper()
    if image.mode in ('RGBA', 'P') and fmt_upper in ('JPEG', 'JPG'):
        image = image.convert('RGB')
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()


def get_image_metadata(image: Image.Image) -> dict[str, Any]:
    """Extract metadata from a PIL Image.
    
    Args:
        image: PIL Image instance
        
    Returns:
        Dictionary containing image metadata (width, height, format, mode)
    """
    return {
        "width": image.width,
        "height": image.height,
        "format": image.format or "UNKNOWN",
        "mode": image.mode,
    }


__all__ = [
    "validate_image_file",
    "load_image",
    "resize_image_for_api",
    "image_to_bytes",
    "get_image_metadata",
]
