from http import cookiejar
import pickle
import re
from datetime import datetime, timedelta

from lxml.html import fragment_fromstring
from selection import XpathSelector
from weblib.etree import drop_node, get_node_text

from ..config import log


def filter_non_printable(string):
	"""
	:param string:
	:return:
	"""
	return ''.join([c for c in string if ord(c) > 31 or ord(c) == 9])


def node_to_selector(node):
	"""
	:param node:
	:return:
	"""
	res = XpathSelector(fragment_fromstring(node))
	return res


def save_cookies(requests_cookiejar, filename):
	"""
	:param requests_cookiejar:
	:param filename:
	:return:
	"""
	with open(filename, 'wb') as f:
		pickle.dump(requests_cookiejar, f)


def load_cookies(filename):
	"""
	:param filename:
	:return:
	"""
	with open(filename, 'rb') as f:
		return pickle.load(f)


def load_cookies_human(filename):
	"""
	:param filename:
	:return:
	"""
	cook = cookiejar.MozillaCookieJar(filename)
	cook.load()
	return cook


def xpath_cls_str(classname):
	"""
	:param classname:
	:return:
	"""
	xpathstr = '[contains(concat(" ", normalize-space(@class), " "), " %s ")' % classname
	return xpathstr


def _xpath_cls_repl(path):
	"""
	:param path:
	:return:
	"""
	rex = re.compile('@class=[\"|\']([\\w\\d-_]*)[\"|\']')
	res = re.findall(rex, path)
	for r in res:
		sub = '[@class=["|\']%s["|\']' % r
		repl = xpath_cls_str(r)
		path = re.sub(sub, repl, path)
	return path


def xpath_cls_repl(path):
	"""
	:param path:
	:return:
	"""
	try:
		if isinstance(path, list):
			_L = []
			for p in path:
				r = _xpath_cls_repl(p)
				_L.append(r)
			return _L
		elif isinstance(path, str):
			return _xpath_cls_repl(path)
		else:
			log('Exception', path)
			return None
	except Exception as ex:
		log(f'Exception', ex, level='warning')
		return None


months = [
	'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
	'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
]


def parse_datetime(date: str):
	"""
	# 23 декабря в 13:37
	# 17 октября 2016 в 19:12
	# 25.12.17 в 12:12
	# вчера в 10:06
	# сегодня в 10:06
	
	:param date:
	:return:
	"""
	parts = list(filter(None, date.split(' ')))
	if parts[0] == 'сегодня':
		publishdate = datetime.today().date()
	elif parts[0] == 'вчера':
		publishdate = (datetime.now() - timedelta(days=1)).date()
	else:
		if len(parts) == 5:
			datestring = parts[0] + '-' + str(months.index(parts[1]) + 1) + '-' + str(parts[2])
		elif len(parts) == 4:
			datestring = parts[0] + '-' + str(months.index(parts[1]) + 1)
			if parts[2] == 'в':
				datestring = datestring + '-' + str(datetime.today().year)
			else:
				datestring = datestring + '-' + parts[2]
		else:
			dateparts = parts[0].split('.')
			dateparts[2] = '20' + dateparts[2]
			datestring = '-'.join(dateparts)
		publishdate = datetime.strptime(datestring, '%d-%m-%Y').date()
	publishdate = str(publishdate) + ' ' + parts[-1]
	return publishdate


def parse_views_count(count_str: str):
	"""
	:param count_str:
	:return:
	"""
	coeff = 1
	coeff2 = 1
	if count_str[len(count_str) - 1] == 'k':
		coeff = 1000
		coeff2 = 100
		count_str = count_str[0:len(count_str) - 1]
	elif count_str[len(count_str) - 1] == 'm':
		coeff = 1000000
		coeff2 = 1000
		count_str = count_str[0:len(count_str) - 1]
	parts = count_str.split(',')
	try:
		count = int(parts[0]) * coeff
		if len(parts) > 1:
			count = count + int(parts[1]) * coeff2
	except Exception as _ex:
		count = 0
	
	return count


def element_links(elm):
	"""
	:param elm:
	:return:
	"""
	try:
		elm_links = elm.select('.//a')
	except Exception as _ex:
		elm_links = []
	
	elm_links_l = []
	
	if elm_links:
		for link in elm_links:
			try:
				link_url = link.select('@href').text()
			except Exception as _ex:
				continue
			try:
				link_text = link.select('text()').text()
			except Exception as _ex:
				try:
					link_text = link.select('./img/@alt').text()
				except Exception as __ex:
					link_text = ''
			try:
				link_img = link.select('./img/@src').text()
			except Exception as _ex:
				link_img = ''
			link_d = {'url': link_url, 'text': link_text, 'img': link_img}
			elm_links_l.append(link_d)
	return elm_links_l


def element_imgs(elm):
	"""
	:param elm:
	:return:
	"""
	try:
		elm_imgs = elm.select('.//img')
	except Exception as _ex:
		elm_imgs = []
	
	elm_imgs_l = []
	if elm_imgs:
		for img in elm_imgs:
			try:
				img_url = img.select('@src').text()
			except Exception as _ex:
				continue
			try:
				img_text = img.select('@alt').text()
			except Exception as _ex:
				img_text = ''
			img_d = {'url': img_url, 'text': img_text}
			elm_imgs_l.append(img_d)
	return elm_imgs_l


def element_codes(elm, xpaths=None):
	"""
	:param elm:
	:param xpaths:
	:return:
	"""
	if xpaths is None:
		xpaths = ['.//code', './/div[@class="oembed"]']
	elm_codes_l = []
	for xpath in xpaths:
		try:
			elm_codes = elm.select(xpath)
		except Exception as _ex:
			elm_codes = []
		if elm_codes:
			for code in elm_codes:
				elm_codes_l.append({
					'text': code.text(),
					'html': code.html(),
				})
	return elm_codes_l


def get_elements(elm, xpath):
	"""
	:param elm:
	:param xpath:
	:return:
	"""
	try:
		target_elms = elm.select(xpath)
	except Exception as _ex:
		target_elms = []
	
	result_elms = []
	if target_elms:
		for quote in target_elms:
			result_elms.append({
				'text': quote.text(),
				'html': quote.html(),
			})
	
	return result_elms


def element_quotes(elm, xpath='.//blockquote'):
	"""
	:param elm:
	:param xpath:
	:return:
	"""
	return get_elements(elm, xpath)


def element_tables(elm, xpath='.//table'):
	"""
	:param elm:
	:param xpath:
	:return:
	"""
	return get_elements(elm, xpath)


def element_drop_node(elm, paths):
	"""
	:param elm:
	:param paths:
	:return:
	"""
	if elm:
		elm_html = elm.html()
		elm_tree = fragment_fromstring(elm_html)
		for path in paths:
			drop_node(elm_tree, path)
		elm_text = get_node_text(elm_tree, smart=True)
		return elm_text
	else:
		return ''
