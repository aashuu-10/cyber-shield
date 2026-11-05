[app]
title = Cyber Shield
package.name = cybershield
package.domain = org.cyphracodes

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,plyer,pyjnius,requests,urllib3,certifi,chardet,idna

orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET,POST_NOTIFICATIONS,VIBRATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.release_artifact = apk

android.presplash_color = #0F172A

[buildozer]
log_level = 2
warn_on_root = 1

android.enable_androidx = True
