import zipfile
import os

def create_zip(zip_name, files_and_dirs):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in files_and_dirs:
            if os.path.isfile(item):
                zipf.write(item, os.path.basename(item))
            elif os.path.isdir(item):
                for root, _, files in os.walk(item):
                    for file in files:
                        if '__pycache__' in root:
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(item))
                        zipf.write(file_path, arcname)

if __name__ == '__main__':
    items_to_zip = ['main.py', 'plugin.json', 'README.md', 'LICENSE', 'Images', 'lib']
    create_zip('Volt-v1.2.8.zip', items_to_zip)
    print("Created Volt-v1.2.8.zip")
