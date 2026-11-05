import os

# 1. Update mobile_app/buildozer.spec
spec_path = "mobile_app/buildozer.spec"
if os.path.exists(spec_path):
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "android.enable_androidx" not in content:
        content += "\nandroid.enable_androidx = True\n"
    else:
        content = content.replace("android.enable_androidx = False", "android.enable_androidx = True")
    
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Updated mobile_app/buildozer.spec with android.enable_androidx = True")

# 2. Create gradle.properties in root and mobile_app
gradle_props = """android.useAndroidX=true
android.enableJetifier=true
org.gradle.jvmargs=-Xmx2048m
"""

with open("gradle.properties", "w", encoding="utf-8") as f:
    f.write(gradle_props)
print("SUCCESS: Created root gradle.properties")

os.makedirs("mobile_app", exist_ok=True)
with open("mobile_app/gradle.properties", "w", encoding="utf-8") as f:
    f.write(gradle_props)
print("SUCCESS: Created mobile_app/gradle.properties")
