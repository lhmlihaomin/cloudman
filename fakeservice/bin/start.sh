#start job here
nohup python -m SimpleHTTPServer &
PID=$!
echo $PID > /tmp/service.pid
