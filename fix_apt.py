import os

workflow_content = """name: Build Cyber Shield Pro APK

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
        sudo apt-get install -y --no-install-recommends \\
          build-essential \\
          git \\
          python3-dev \\
          zlib1g-dev \\
          libssl-dev \\
          libffi-dev \\
          libsqlite3-dev \\
          libncurses5-dev \\
          libncursesw5-dev \\
          libbz2-dev \\
          liblzma-dev \\
          zip \\
          unzip \\
          autoconf \\
          libtool \\
          cmake \\
          pkg-config \\
          ccache

    - name: Install Buildozer & Dependencies
      run: |
        pip install --upgrade pip
        pip install buildozer==1.5.0 cython==0.29.33 kivy==2.3.0 virtualenv

    - name: Build Kivy Python APK
      run: |
        cd mobile_app
        buildozer android debug

    - name: Upload Cyber Shield Pro Matrix APK
      uses: actions/upload-artifact@v4
      with:
        name: CyberShield-Pro-Matrix-APK
        path: mobile_app/bin/*.apk
        retention-days: 30
"""

os.makedirs(".github/workflows", exist_ok=True)
with open(".github/workflows/build.yml", "w", encoding="utf-8") as f:
    f.write(workflow_content)

print("SUCCESS: Updated workflow with conflict-free dependencies!")