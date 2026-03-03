from PIL import Image

def make_green(path, out_path):
    try:
        img = Image.open(path).convert("RGBA")
        data = img.getdata()
        new_data = []
        for item in data:
             # If it's not fully transparent, make it green
            if item[3] > 0:
                # Tint towards a vibrant green (0, 200, 50)
                r = int(item[0] * 0.2)
                g = int(item[1] * 0.2 + 180)
                b = int(item[2] * 0.2 + 50)
                new_data.append((min(255, r), min(255, g), min(255, b), item[3]))
            else:
                new_data.append(item)
        img.putdata(new_data)
        img.save(out_path)
        print(f"Generated {out_path}")
    except Exception as e:
        print(f"Failed {path}: {e}")

make_green("Images/high.png", "Images/high_active.png")
make_green("Images/balanced.png", "Images/balanced_active.png")
make_green("Images/saver.png", "Images/saver_active.png")
