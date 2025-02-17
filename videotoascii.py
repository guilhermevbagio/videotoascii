import argparse
import json
import cv2
import time
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

ASCII_CHARS = " .-=+o#%@"

def downscale_image(image, scale_factor):
    original_width, original_height = image.size
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    return image.resize((new_width, new_height))

def pixel_to_ascii(pixel):
    gray = int((pixel[0] + pixel[1] + pixel[2]) / 3)
    return ASCII_CHARS[int(gray / 32)]

def image_to_ascii(image, scale_factor=0.1):
    image = downscale_image(image, scale_factor)
    image = image.convert("RGB")
    ascii_image = []
    for y in range(image.height):
        row = [pixel_to_ascii(image.getpixel((x, y))) for x in range(image.width)]
        ascii_image.append("".join(row))
    return "\n".join(ascii_image)

def video_to_ascii(video_path, scale_factor=0.1, output_file="ascii_frames.json"):
    cap = cv2.VideoCapture(video_path)
    ascii_frames = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ascii_art = image_to_ascii(image, scale_factor)
        ascii_frames.append(f"< {ascii_art} >")
        
        frame_count += 1
        print(f"Processed frame {frame_count}", end="\r")
    
    cap.release()
    
    with open(output_file, "w") as f:
        json.dump({"frames": ascii_frames}, f, indent=2)
    
    print(f"\nASCII frames saved to {output_file}")

def play_ascii_video(json_file, frame_delay=0.1):
    with open(json_file, "r") as f:
        data = json.load(f)
    
    frames = data.get("frames", [])
    
    for frame in frames:
        print("\033[H\033[J", end="")
        print(frame.strip("< >"))
        time.sleep(frame_delay)

def ascii_to_png(ascii_text, output_path, font_size=20, padding=10):
    lines = ascii_text.strip().split('\n')
    font = ImageFont.load_default()
    char_width = font_size * 0.4
    char_height = font_size * 0.4
    
    width = int(max(len(line) for line in lines) * char_width + 2 * padding)
    height = int(len(lines) * char_height + 2 * padding)
    
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    
    y = padding
    for line in lines:
        x = padding
        for char in line:
            draw.text((x, y), char, font=font, fill='white')
            x += char_width
        y += char_height
    
    image.save(output_path)
    return image

def convert_json_to_pngs(json_file, output_folder="ascii_frames_png", font_size=20):
    os.makedirs(output_folder, exist_ok=True)
    
    with open(json_file, "r") as f:
        data = json.load(f)
    
    frames = data.get("frames", [])
    
    print(f"Converting {len(frames)} frames to PNG...")
    for i, frame in enumerate(frames):
        ascii_frame = frame.strip("< >")
        output_path = os.path.join(output_folder, f"frame_{i:04d}.png")
        ascii_to_png(ascii_frame, output_path, font_size=font_size)
        print(f"Processed frame {i+1}/{len(frames)}", end="\r")
    
    print(f"\nPNG frames saved to {output_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a video to ASCII frames stored in JSON, play an ASCII video, or convert ASCII frames to PNG.")
    parser.add_argument("video_path", nargs="?", help="Path to the video file")
    parser.add_argument("--scale", type=float, default=0.1, help="Scale factor for resizing frames (default: 0.1)")
    parser.add_argument("--output", type=str, default="ascii_frames.json", help="Output JSON file (default: ascii_frames.json)")
    parser.add_argument("--play", type=str, help="Path to the ASCII JSON file to play")
    parser.add_argument("--delay", type=float, default=0.1, help="Frame delay in seconds (default: 0.1)")
    parser.add_argument("--to-png", type=str, help="Convert ASCII JSON file to PNG frames")
    parser.add_argument("--png-output", type=str, default="ascii_frames_png", help="Output folder for PNG frames")
    parser.add_argument("--font-size", type=int, default=20, help="Font size for PNG conversion (default: 20)")
    
    args = parser.parse_args()
    
    if args.to_png:
        convert_json_to_pngs(args.to_png, args.png_output, args.font_size)
    elif args.play:
        play_ascii_video(args.play, frame_delay=args.delay)
    elif args.video_path:
        video_to_ascii(args.video_path, scale_factor=args.scale, output_file=args.output)
    else:
        print("Please provide either a video file to convert, a JSON file to play, or a JSON file to convert to PNG.")
