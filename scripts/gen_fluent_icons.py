import os
import requests
import cairosvg

ICONS = {
    'app.png': 'https://api.iconify.design/fluent/flash-24-filled.svg?color=%23FFBF00&width=100&height=100',
    'high.png': 'https://api.iconify.design/fluent/rocket-24-filled.svg?color=%23FF4500&width=100&height=100',
    'balanced.png': 'https://api.iconify.design/fluent/scales-24-filled.svg?color=%231E90FF&width=100&height=100',
    'saver.png': 'https://api.iconify.design/fluent/leaf-two-24-filled.svg?color=%2332CD32&width=100&height=100'
}

def generate_fluent_icons():
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'Images')
    os.makedirs(images_dir, exist_ok=True)
    
    for filename, url in ICONS.items():
        print(f"Downloading {filename}...")
        response = requests.get(url)
        if response.status_code == 200:
            svg_data = response.content
            out_path = os.path.join(images_dir, filename)
            cairosvg.svg2png(bytestring=svg_data, write_to=out_path)
            print(f"Saved {filename} ({len(svg_data)} bytes SVG)")
        else:
            print(f"Error fetching {url}: {response.status_code}")

if __name__ == '__main__':
    generate_fluent_icons()
