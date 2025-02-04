import argparse
import json
import cv2
import time
from PIL import Image

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
        print("\033[H\033[J", end="")  # Clear screen
        print(frame.strip("< >"))
        time.sleep(frame_delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a video to ASCII frames stored in JSON or play an ASCII video.")
    parser.add_argument("video_path", nargs="?", help="Path to the video file")
    parser.add_argument("--scale", type=float, default=0.1, help="Scale factor for resizing frames (default: 0.1)")
    parser.add_argument("--output", type=str, default="ascii_frames.json", help="Output JSON file (default: ascii_frames.json)")
    parser.add_argument("--play", type=str, help="Path to the ASCII JSON file to play")
    parser.add_argument("--delay", type=float, default=0.1, help="Frame delay in seconds (default: 0.1)")
    
    args = parser.parse_args()
    
    if args.play:
        play_ascii_video(args.play, frame_delay=args.delay)
    elif args.video_path:
        video_to_ascii(args.video_path, scale_factor=args.scale, output_file=args.output)
    else:
        print("Please provide either a video file to convert or a JSON file to play.")
