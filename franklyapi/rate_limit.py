from app import redis_rate_limit
import time


def get_request_key(url, ip):
	url_path = url.split('api.frankly.me')[1].split('?')[0]
	key = '{url_path}|||{ip}'.format(url_path=url_path, ip=ip)
	return key

def check_allowed(url, ip):

	pass

def log_request(url, ip):
	
	pass

