import re
import shutil
import socket
import time
from multiprocessing.dummy import Pool as tPool
from urllib.parse import urlsplit

import requests
from ..config import log
from requests.auth import HTTPProxyAuth
from tldextract import extract

HOST = 'localhost'


def get_domain_from_url(url):
	"""
	:param url:
	:return:
	"""
	domain = extract(url).fqdn
	return domain


def get_site_from_url(url):
	"""
	:param url:
	:return:
	"""
	base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
	return base_url


def check_proxy(proxy, url='https://google.com/', timeout=10):
	"""
	:param proxy:
	:param url:
	:param timeout:
	:return:
	"""
	if proxy.get('login') and proxy.get('pas'):
		auth = [proxy['login'], proxy['pas']]
	else:
		auth = None
	_r = check_url(url=url, proxy="{ip}:{port}".format(**proxy), timeout=timeout, auth=auth, proxy_type=proxy['typ'])
	return proxy if _r else False


def check_proxys(proxys, url='https://google.com/', timeout=10):
	"""
	:param proxys: ['url:port',]
	:param url:
	:param timeout:
	:return:
	"""
	_res = []
	for proxy in proxys:
		_r = check_proxy(proxy=proxy, url=url, timeout=timeout)
		if _r:
			_res.append(proxy)
		else:
			log('Fail', proxy)
	return _res


def request_prepare_proxy(proxy=None, proxy_type='http', auth=None):
	"""
	:param proxy: 'url:port'
	:param proxy_type: http, socks5
	:param auth: (login, password)
	:return:
	"""
	proxies = None
	if proxy:
		proxy_str = proxy
		if auth:
			proxy_str = f'{auth[0]}:{auth[1]}@{proxy_str}'
		
		if proxy_type in ['socks', 'socks5']:
			proxy_str = 'socks5://' + proxy_str
		elif proxy_type in ['socksh', 'socks5h']:
			proxy_str = 'socks5h://' + proxy_str
		elif proxy_type == 'http':
			proxy_str = 'http://' + proxy_str
		else:
			proxy_str = None
		
		if proxy_str:
			proxies = {
				'http': proxy_str,
				'https': proxy_str
			}
	return proxies


def check_url(url='https://google.com/', proxy=None, timeout=5, auth=None, proxy_type='http'):
	"""
	:param url:
	:param proxy: 'url:port'
	:param timeout:
	:param auth: (login, password)
	:param proxy_type: http, socks5
	:return:
	"""
	url = prepend_http(url)
	proxies = request_prepare_proxy(proxy, proxy_type, auth)
	try:
		r = requests.get(url, timeout=timeout, proxies=proxies)
		if r.status_code == requests.codes.ok:
			res = True
		else:
			log('r.status_code', r.status_code)
			res = False
		return res
	except Exception as ex:
		log('proxies ex', proxies, ex)
		return False


def get_file_from_url(url='https://google.com/', proxy=None, timeout=5, auth=None, proxy_type='http', cookies=None, user_agent=None):
	"""
	:param url:
	:param proxy: 'url:port'
	:param timeout:
	:param auth: (login, password)
	:param proxy_type: http, socks5
	:param cookies:
	:param user_agent:
	:return:
	"""
	s = requests.Session()
	if cookies is not None:
		for cookie in cookies:
			try:
				s.cookies.set(cookie['name'], cookie['value'])
			except Exception as ex:
				log('save url file cookies ex', ex)
	if user_agent is not None:
		s.headers.update({'User-Agent': 'user_agent'})
	url = prepend_http(url)
	proxies = request_prepare_proxy(proxy, proxy_type, auth)
	try:
		r = requests.get(url, timeout=timeout, proxies=proxies, stream=True)
	except Exception as ex:
		log('save url file ex', ex)
		r = False
	if r and r.status_code == 200:
		return r
	else:
		return None


def save_file_from_url(url='https://google.com/', proxy=None, timeout=5, auth=None, proxy_type='http', file_name=None, cookies=None, user_agent=None):
	"""
	скачивает файл по урлу
	:param url:
	:param proxy: 'url:port'
	:param timeout:
	:param auth: (login, password)
	:param proxy_type: http, socks5
	:param file_name:
	:param cookies:
	:param user_agent:
	:return:
	"""
	r = get_file_from_url(url=url, proxy=proxy, timeout=timeout, auth=auth, proxy_type=proxy_type, cookies=cookies, user_agent=user_agent)
	if r and r.status_code == 200:
		file_name = file_name if file_name else 'saved_file_' + str(time.time()) + '.png'
		with open(file_name, 'wb') as f:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, f)
		return file_name
	else:
		return None


def prepend_http(url):
	"""
	:param url:
	:return:
	"""
	# regx = re.compile('^(?:f|ht)tps?://','i')
	regx = re.compile('https?://')
	result = regx.match(url)
	# print(result)
	if not result:
		url = "http://" + url
	return url


def check_ports(ports=None):
	"""
	# Создаем список портов, которые мы хотим просканирвать
	# ports = [21, 22, 23, 25, 38, 43, 80, 109, 110, 115, 118, 119, 143,
	# 194, 220, 443, 540, 585, 591, 1112, 1433, 1443, 3128, 3197,
	# 3306, 4000, 4333, 5100, 5432, 6669, 8000, 8080, 9014, 9200]
	# Теперь в цикле перебераем все указаные порты
	:param ports:
	:return:
	"""
	if ports is None:
		ports = [7834]
	for port in ports:
		check_port(port)


def check_port(port=7834):
	"""
	:param port:
	:return:
	"""
	# Создаем новый сокет
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Устанавливаем таймаут, чтоб скрипт не зависал если попал
	# на открытый порт
	sock.settimeout(1)
	try:
		# Пробуем подключится
		sock.connect((HOST, port))
	except Exception as _ex:
		# Если возникло исключение -- порт закрыт
		print("Порт %s закрыт" % port)
	try:
		# Если порт открыт - пробуем прочитать с него порцию информации
		result = sock.recv(1024)
		# если что-то удалось прочитать, выводим это
		print("Читаемый %s port: %s" % port, result)
		r = False
	except Exception as _ex:
		# Если ничего прочитать не удалось -- просто выводим
		# информацию что порт открыт
		print("Порт %s открыт." % port)
		r = True
	# закрываем сокет.
	sock.close()
	return r


def open_url(url='http://www.google.com/', timeout=5, proxy_addres=False, proxy_login=None, proxy_pass=None, attr=None):
	"""
	:param url:
	:param timeout:
	:param proxy_addres:
	:param proxy_login:
	:param proxy_pass:
	:param attr:
	:return:
	"""
	url = prepend_http(url)
	if proxy_addres:
		proxies = {
			'http': proxy_addres,
			'https': proxy_addres
		}
	else:
		proxies = None
	if proxy_login and proxy_pass:
		auth = HTTPProxyAuth(proxy_login, proxy_pass)
	else:
		auth = None
	r = requests.get(url, timeout=timeout, proxies=proxies, auth=auth)
	if attr:
		return getattr(r, attr)
	else:
		return r


def check_proxys_pool(url, proxys, timeout=15, workers=None):
	"""
	:param url:
	:param proxys:
	:param timeout:
	:param workers:
	:return:
	"""
	_res = []
	max_worker = len(proxys)
	if workers:
		max_worker = min(max_worker, workers)
	with tPool(max_worker) as executor:
		multiple_results = [executor.apply_async(check_proxy, args=(proxys[i], url, timeout,)) for i in range(len(proxys))]
		_res = [res.get() for res in multiple_results]
	try:
		proxy = list(filter(lambda x: x is not None, _res))
	except Exception as _ex:
		proxy = []
	return proxy


def parse_ip(ip):
	"""
	:param ip:
	:return:
	"""
	return list(re.findall(r'[0-9]+(?:\.[0-9]+){3}', ip))
