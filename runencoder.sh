for count in {0..59}
do
	num=`ps -ef|grep python | grep celery|grep encoding|wc -l`
	if [ $num -lt 1 ]; then
		cd '/home/ubuntu/franklysql/franklyapi'
		echo "$num restarting encoder worker"
		#alertAdmin 
		/usr/bin/python /usr/local/bin/celery worker --concurrency=2  -Q encoding --app=async_encoder -l info -f /var/celery_encoding.log --pid /var/celery_encoding.pid -P gevent &
	fi
	sleep 1
done