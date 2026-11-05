import os

# 1. Update Workflow to Disable Cache for a Clean Build
workflow_code = """name: Build Android APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.10
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'

    - name: Install System Dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \\
          build-essential \\
          git \\
          python3-dev \\
          ffmpeg \\
          libsdl2-dev \\
          libsdl2-image-dev \\
          libsdl2-mixer-dev \\
          libsdl2-ttf-dev \\
          libportmidi-dev \\
          libswscale-dev \\
          libavformat-dev \\
          libavcodec-dev \\
          zlib1g-dev \\
          libgstreamer1.0-dev \\
          gstreamer1.0-plugins-base \\
          gstreamer1.0-plugins-good \\
          libsqlite3-dev \\
          sqlite3 \\
          bzip2 \\
          libbz2-dev \\
          libssl-dev \\
          openssl \\
          libgdbm-dev \\
          libgdbm-compat-dev \\
          liblzma-dev \\
          libffi-dev \\
          libncurses-dev \\
          zip \\
          unzip \\
          autoconf \\
          libtool \\
          cmake \\
          pkg-config

    - name: Install Buildozer & Cython
      run: |
        pip install --upgrade pip
        pip install buildozer==1.5.0 cython==0.29.33 kivy==2.3.0 virtualenv

    - name: Clean & Build Fresh APK with Buildozer
      run: |
        cd mobile_app
        buildozer android clean
        buildozer android debug

    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: CyberShield-Pro-v2-APK
        path: mobile_app/bin/*.apk
        retention-days: 30
"""

os.makedirs(".github/workflows", exist_ok=True)
with open(".github/workflows/build_apk.yml", "w", encoding="utf-8") as f:
    f.write(workflow_code)
print("SUCCESS: Updated workflow to force clean build.")

# 2. Update Version in buildozer.spec to 2.0.0
spec_code = """[app]
title = Cyber Shield Pro
package.name = cybershieldpro
package.domain = org.cyphracodes
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 2.0.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,plyer,pyjnius,requests,urllib3,certifi,chardet,idna
orientation = portrait
osx.kivy_version = 2.3.0

fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET,POST_NOTIFICATIONS,VIBRATE,CALL_PHONE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.release_artifact = apk
android.enable_androidx = True

android.presplash_color = #080F0A
"""

with open("mobile_app/buildozer.spec", "w", encoding="utf-8") as f:
    f.write(spec_code)
print("SUCCESS: Updated buildozer.spec version to 2.0.0.")