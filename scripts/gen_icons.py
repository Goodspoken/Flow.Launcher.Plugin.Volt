import os
from PIL import Image

def create_color_icon(filename, color):
    # 100x100 solid color icon
    img = Image.new('RGB', (100, 100), color=color)
    img.save(filename)

if __name__ == "__main__":
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'Images'), exist_ok=True)
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'Images')
    create_color_icon(os.path.join(images_dir, 'app.png'), 'grey')
    create_color_icon(os.path.join(images_dir, 'high.png'), '#e74c3c')       # Red
    create_color_icon(os.path.join(images_dir, 'balanced.png'), '#3498db')   # Blue
    create_color_icon(os.path.join(images_dir, 'saver.png'), '#2ecc71')      # Green
