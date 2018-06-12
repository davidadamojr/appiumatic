ADB_PATH=$1
DEVICE=`$ADB_PATH devices | grep emulator | head -n 1 | awk '{print $1}'`
$ADB_PATH -s $DEVICE emu kill