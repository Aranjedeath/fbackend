for count in {0..59}
do
	num=`ps -ef|grep python | grep celery|grep periodic|wc -l`
	if [ $num -lt 1 ]; then
		cd '/home/ubuntu/franklysql/franklyapi'
		echo "$num restarting periodic celery worker"
		#alertAdmin 
		#/usr/bin/python /usr/local/bin/celery worker -B  -s /tmp/celery_scheduler --concurrency=2  -Q periodic
		#--app=periodic_tasks -l info -f /tmp/periodic_tasks.log --pid /tmp/periodic_tasks.pid &
        /usr/bin/python /usr/local/bin/celery worker -A periodic_tasks -s /tmp/celery_scheduler -Q periodic --concurrency 2 --loglevel=DEBUG -f /tmp/periodic_tasks.log --pid /tmp/periodic_tasks.pid --beat &


	fi
	sleep 1
done