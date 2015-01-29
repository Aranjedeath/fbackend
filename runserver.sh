for count in {0..59}
do
	num=`ps -ef|grep python|grep gunicorn|grep app|wc -l`
	if [ $num -lt 1 ]; then
		cd '/home/ubuntu/franklysql/'
		echo "$num restarting urgent worker"
		#alertAdmin 
		/bin/bash guni
	fi
	sleep 1
done