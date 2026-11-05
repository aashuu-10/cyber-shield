[app]
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
