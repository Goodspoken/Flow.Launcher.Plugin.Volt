import os
from PIL import Image

def create_color_icon(filename, color):
    # 100x100 solid color icon
    img = Image.new('RGB', (100, 100), color=color)
    img.save(filename)

if __name__ == "__main__":
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'Images'), exist_ok=True)
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'Images')
    create_color_icon(os.path.join(images_dir, 'app.png'), '#FFBF00')      # Amber/Volt
    create_color_icon(os.path.join(images_dir, 'high.png'), '#FF4500')     # OrangeRed (Performance)
    create_color_icon(os.path.join(images_dir, 'balanced.png'), '#1E90FF') # DodgerBlue (Balanced)
    create_color_icon(os.path.join(images_dir, 'saver.png'), '#32CD32')    # LimeGreen (Eco)
