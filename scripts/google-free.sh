#!/usr/bin/env bash

sed -i -e '$aGOOGLE_FREE=1' .env.release

#------------------------------------
# Remove Android Remote Notifications
#------------------------------------

yarn remove react-native-notifications
rm android/app/google-services.json
sed -i -e '/com.wix.reactnativenotifications.RNNotificationsPackage;/d' android/app/src/main/java/im/status/ethereum/MainApplication.java
sed -i -e '/com.google.gms:google-services/d' android/build.gradle
sed -i -e '/react-native-notifications/,+2d' android/settings.gradle
FIREBASE_LINE=`grep -n 'com.google.firebase.messaging.default_notification_icon' android/app/src/main/AndroidManifest.xml | cut -d : -f 1`
sed -i -e "$((FIREBASE_LINE-1)),+5d" android/app/src/main/AndroidManifest.xml
sed -i -e 's/\["react-native-notifications" :refer (Notifications)\]//' src/status_im/notifications/android_remote.cljs
