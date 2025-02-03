import argparse
from PIL import Image

def downscale_image(image_path, scale_factor):
    image = Image.open(image_path)
    
    original_width, original_height = image.size
    
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    
    downscaled_image = image.resize((new_width, new_height))
    return downscaled_image

def pixel_to_ascii(pixel):
    gray = int((pixel[0] + pixel[1] + pixel[2]) / 3)
    
    ascii_chars = "@%#*+=-:. "
    
    return ascii_chars[int(gray / 32)]

def image_to_ascii(image_path, scale_factor=0.1):
    image = downscale_image(image_path, scale_factor)
    
    image = image.convert("RGB")
    
    ascii_image = []
    
    for y in range(image.height):
        row = []
        for x in range(image.width):
            pixel = image.getpixel((x, y))
            row.append(pixel_to_ascii(pixel))
        ascii_image.append("".join(row))
    
    return "\n".join(ascii_image)

def save_ascii_to_file(ascii_image, output_file="ascii_image.txt"):
    with open(output_file, "w") as f:
        f.write(ascii_image)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an image to ASCII art.")
    parser.add_argument("image_path", help="Path to the image to convert")
    parser.add_argument("--scale", type=float, default=0.1, help="Scale factor to resize the image (default: 0.1)")
    parser.add_argument("--output", type=str, default="ascii_image.txt", help="Output file to save the ASCII art (default: ascii_image.txt)")
    
    args = parser.parse_args()
    
    ascii_art = image_to_ascii(args.image_path, scale_factor=args.scale)
    
    save_ascii_to_file(ascii_art, output_file=args.output)
    
    print(f"ASCII art saved to {args.output}")
