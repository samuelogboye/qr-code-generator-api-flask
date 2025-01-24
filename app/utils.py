import qrcode
from io import BytesIO
from typing import Optional
from PIL import Image

def generate_qr_code(url: str, size: int = 10) -> Optional[bytes]:
    """
    Generate a QR code for the given URL
    
    Args:
        url (str): The URL to encode in the QR code
        size (int): The size of the QR code (default: 10)
        
    Returns:
        bytes: The QR code image in PNG format
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        return img_buffer.getvalue()
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return None 