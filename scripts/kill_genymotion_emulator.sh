ps -A | grep 'player' | awk '{print $1}' | xargs kill
ps -A | grep 'VBoxHeadless' | awk '{print $1}' | xargs kill