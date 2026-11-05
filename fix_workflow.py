import os

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

    - name: Cache Buildozer Global Directory
      uses: actions/cache@v4
      with:
        path: ~/.buildozer
        key: ${{ runner.os }}-buildozer-${{ hashFiles('mobile_app/buildozer.spec') }}
        restore-keys: |
          ${{ runner.os }}-buildozer-

    - name: Build APK with Buildozer
      run: |
        cd mobile_app
        buildozer android debug

    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: CyberShield-APK
        path: mobile_app/bin/*.apk
        retention-days: 30
"""

os.makedirs(".github/workflows", exist_ok=True)
with open(".github/workflows/build_apk.yml", "w", encoding="utf-8") as f:
    f.write(workflow_code)

print("SUCCESS: Fixed typo in .github/workflows/build_apk.yml")
