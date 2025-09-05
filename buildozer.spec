[app]
title = Organizer Budzetu
package.name = organizerbudzetu
package.domain = org.budgetapp

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

requirements = python3,kivy==2.1.0,openssl

orientation = portrait
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 28

fullscreen = 0
log_level = 1

# CRITICAL: Skip downloads and use prebuilt
android.skip_update = True
android.accept_sdk_license = True

# Optimize build
android.arch = armeabi-v7a
p4a.branch = master

[buildozer]
log_level = 1
