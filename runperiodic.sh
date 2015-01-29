for count in {0..59}
do
	num=`ps -ef|grep python | grep celery|grep encoding|wc -l`
	if [ $num -lt 1 ]; then
		cd '/home/ubuntu/franklysql/franklyapi'
		echo "$num restarting periodic celery worker"
		#alertAdmin 
		/usr/bin/python /usr/local/bin/celery worker --concurrency=2  -Q encoding --app=periodic_tasks -l info -f /var/periodic_tasks.log --pid /var/periodic_tasks.pid -P gevent &
	fi
	sleep 1
done