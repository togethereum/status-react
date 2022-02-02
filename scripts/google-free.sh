#!/usr/bin/env bash

sed -i -e '$aGOOGLE_FREE=1' .env.release

#------------------------------------
# Remove Android Remote Notifications
#------------------------------------

yarn remove react-native-notifications
rm android/app/google-services.json
sed -i -e 's/\["react-native-notifications" :refer (Notifications)\]//' src/status_im/notifications/android_remote.cljs
