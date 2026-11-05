import os

count = 0
for root, dirs, files in os.walk('.'):
    if '.git' in root or '.buildozer' in root or 'build' in root:
        continue
    for file in files:
        if file.endswith(('.java', '.gradle', '.kts', '.properties', '.xml', '.py', '.yml', '.yaml')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                
                # Check for UTF-8 BOM byte sequence (0xEF, 0xBB, 0xBF)
                if content.startswith(b'\xef\xbb\xbf'):
                    content = content[3:]
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    print(f"Cleaned BOM header from: {filepath}")
                    count += 1
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

print(f"\nSUCCESS: Cleaned BOM header from {count} files!")
