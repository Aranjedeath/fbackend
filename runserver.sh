for count in 1 2 3 4 5 6 7 8 9 10 11 12
do
	num=`ps -ef|grep python|grep gunicorn|grep app|wc -l`
	if [ $num -lt 1 ]; then
		cd '/home/ubuntu/franklysql/'
		echo "$num restarting urgent worker"
		#alertAdmin 
		/bin/bash guni
	fi
	sleep 5
done