# stego.py

from PIL import Image

DELIMITER = b"<<<END>>>"  # marks where hidden data stops

def _bytes_to_bits(data: bytes) -> str:
    return ''.join(format(byte, '08b') for byte in data)

def _bits_to_bytes(bits: str) -> bytes:
    byte_chunks = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return bytes(int(b, 2) for b in byte_chunks)

def hide_data(image_path: str, data: bytes, output_path: str):
    """
    Hides `data` (your encrypted message bytes) inside the image
    at image_path, and saves the result to output_path.
    """
    img = Image.open(image_path)
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size

    payload = data + DELIMITER
    bits = _bytes_to_bits(payload)

    max_capacity = width * height * 3  # 1 bit per color channel
    if len(bits) > max_capacity:
        raise ValueError(
            f"Message too large for this image. "
            f"Need {len(bits)} bits, image only holds {max_capacity}."
        )

    bit_index = 0
    for y in range(height):
        for x in range(width):
            if bit_index >= len(bits):
                break
            r, g, b = pixels[x, y]
            channels = [r, g, b]
            for c in range(3):
                if bit_index < len(bits):
                    channels[c] = (channels[c] & ~1) | int(bits[bit_index])
                    bit_index += 1
            pixels[x, y] = tuple(channels)
        if bit_index >= len(bits):
            break

    img.save(output_path, "PNG")  # PNG is required — it's lossless

def extract_data(image_path: str) -> bytes:
    """
    Extracts hidden data from an image that was processed with hide_data().
    """
    img = Image.open(image_path)
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size

    bits = ""
    delimiter_bits = _bytes_to_bits(DELIMITER)

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            for value in (r, g, b):
                bits += str(value & 1)
                if bits.endswith(delimiter_bits):
                    payload_bits = bits[:-len(delimiter_bits)]
                    return _bits_to_bytes(payload_bits)

    raise ValueError("No hidden data found (or delimiter missing/corrupted).")

