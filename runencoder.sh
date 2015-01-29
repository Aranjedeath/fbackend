for count in 1 2 3 4 5 6 7 8 9 10 11 12
do
	num=`ps -ef|grep python | grep celery|grep cel_tasks|grep encoding|wc -l`
	if [ $num -lt 1 ]; then
		cd '/home/ubuntu/franklysql/franklyapi'
		echo "$num restarting encoder worker"
		#alertAdmin 
		/usr/bin/python /usr/local/bin/celery worker --concurrency=2  -Q encoding --app=async_encoder -l info -f /var/celery_encoding.log --pid /var/celery_encoding.pid -P gevent &
	fi
	sleep 5
done