for count in {0..59}
do
	num=`ps -ef|grep python | grep celery|grep encoding|wc -l`
	if [ $num -lt 1 ]; then
		cd '/home/ubuntu/franklysql/franklyapi'
		echo "$num restarting encoder worker"
		#alertAdmin 
		/usr/bin/python /usr/local/bin/celery worker --concurrency=1 --autoreload --maxtasksperchild=10 -Ofair  -Q encoding --app=async_encoder -l info -f /tmp/celery_encoding.log --pid /tmp/celery_encoding.pid&
	fi
	num=`ps -ef|grep python | grep celery|grep encoding_high_priority|wc -l`
	if [ $num -lt 1 ]; then
		cd '/home/ubuntu/franklysql/franklyapi'
		echo "$num restarting encoder worker"
		#alertAdmin 
		/usr/bin/python /usr/local/bin/celery worker --concurrency=2 --autoreload --maxtasksperchild=10 -Ofair  -Q encoding_high_priority --app=async_encoder -l info -f /tmp/celery_encoding_high.log --pid /tmp/celery_encoding_high.pid&
	fi
	num=`ps -ef|grep python | grep celery|grep "-Q encoding_low_priority"|wc -l`
	if [ $num -lt 1 ]; then
		cd '/home/ubuntu/franklysql/franklyapi'
		echo "$num restarting encoder worker"
		#alertAdmin 
		/usr/bin/python /usr/local/bin/celery worker --concurrency=2 --autoreload --maxtasksperchild=10 -Ofair  -Q encoding_low_priority --app=async_encoder -l info -f /tmp/celery_encoding_low.log --pid /tmp/celery_encoding_low.pid&
	fi
	num=`ps -ef|grep python | grep celery|grep encoding_retry|wc -l`
	if [ $num -lt 1 ]; then
		cd '/home/ubuntu/franklysql/franklyapi'
		echo "$num restarting encoder worker"
		#alertAdmin 
		/usr/bin/python /usr/local/bin/celery worker --concurrency=2 --autoreload --maxtasksperchild=10 -Ofair  -Q encoding_retry,encoding_low_priority --app=async_encoder -l info -f /tmp/celery_encoding_retry.log --pid /tmp/celery_encoding_retry.pid&
	fi
	sleep 1
done


