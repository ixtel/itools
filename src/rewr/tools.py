import codecs
import json
import os
import pickle
import shelve
from collections import OrderedDict
from os.path import isfile
from typing import Union

from .big import read_big
from ..config import log


class Pickle:
	def __init__(self, path):
		"""
		:param path:
		"""
		self.path = path
		os.makedirs(os.path.dirname(path), exist_ok=True)
	
	def read(self):
		"""
		:return:
		"""
		if isfile(self.path):
			with open(self.path, 'rb') as fp:
				obj = pickle.load(fp)
			return obj
		else:
			return {}
	
	def write(self, obj):
		"""
		:param obj:
		:return:
		"""
		with open(self.path, 'wb') as fp:
			pickle.dump(obj, fp)


class Json:
	def __init__(self, path):
		"""
		:param path:
		"""
		self.path = path
		os.makedirs(os.path.dirname(path), exist_ok=True)
	
	def read(self, data: Union[dict, list, OrderedDict] = None, encoding='utf-8', *args, **kwargs) -> Union[dict, list, OrderedDict]:
		"""
		:param encoding:
		:param data:
		:return:
		"""
		if data is None:
			data = {}
		if isfile(self.path):
			with open(self.path, 'r', encoding=encoding) as fp:
				fpstr = fp.read()
			data = json.loads(fpstr, *args, **kwargs) if len(fpstr) else {}
		return data
	
	def get_oredered_dict(self, encoding='utf-8', *args, **kwargs) -> Union[dict, OrderedDict]:
		"""
		:return: Union[dict, OrderedDict]
		"""
		obj = self.read(dict(), encoding=encoding, *args, **kwargs)
		if obj:
			return OrderedDict(sorted(obj.items(), key=lambda x: x, reverse=False))
		return obj
	
	def write(self, obj: Union[dict, list, OrderedDict], encoding='utf-8', *args, **kwargs):
		"""
		:param encoding:
		:param obj: Union[dict, list, OrderedDict]
		:param args:
		:param kwargs:
		:return:
		"""
		with open(self.path, 'w', encoding=encoding) as fp:
			json.dump(obj, fp, indent=4, *args, **kwargs)


def file_to_text(path, rw='r', encoding='utf-8'):
	"""
	:param path:
	:param rw:
	:param encoding:
	:return:
	"""
	with codecs.open(path, rw, encoding=encoding) as f:
		text = f.read()
	f.close()
	return text


def text_to_file(text, path, rw='w', encoding='utf-8'):
	"""
	:param text:
	:param path:
	:param rw:
	:param encoding:
	:return:
	"""
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with codecs.open(path, rw, encoding=encoding) as f:
		f.write(text)
	f.close()


def file_to_bytes(path, rw='rb'):
	"""
	:param path:
	:param rw:
	:return:
	"""
	with codecs.open(path, rw) as f:
		text = f.read()
	f.close()
	return text


def bytes_to_file(text, path, rw='wb'):
	"""
	:param text:
	:param path:
	:param rw:
	:return:
	"""
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with codecs.open(path, rw) as f:
		f.write(text)
	f.close()


def file_to_arr(path, ext='txt', rw='r', encoding='utf-8-sig'):
	"""
	:param path:
	:param ext:
	:param rw:
	:param encoding:
	:return:
	"""
	if not path.endswith('.%s' % ext):
		path += ".%s" % ext
	with codecs.open(path, rw, encoding=encoding) as f:
		content = f.read().strip()
	f.close()
	try:
		return content.splitlines()
	except Exception as _ex:
		return []


def json_to_file(data, path):
	"""
	:param data:
	:param path:
	:return:
	"""
	Json(path).write(data)


def arr_to_file(arr_in, path, ext: Union[None, str] = 'txt', rw='w', encoding: Union[None, str] = 'utf-8', batch=True):
	"""
	:param arr_in:
	:param path:
	:param ext:
	:param rw:
	:param encoding:
	:param batch:
	:return:
	"""
	if ext is not None and not path.endswith('.' + ext):
		path += ".%s" % ext
	os.makedirs(os.path.dirname(path), exist_ok=True)
	new_line = '\n'
	if rw.find('b') != -1:
		new_line = b'\n'
		encoding = None
	elif encoding is None:
		rw += 'b'
		new_line = b'\n'
	with codecs.open(path, rw, encoding=encoding) as f:
		if encoding is None:
			try:
				f.writelines(arr_in)
			except Exception as ex:
				print(f'Exception writelines encoding is None', ex)
				pass
		else:
			try:
				if batch:
					l1 = map(lambda x: x + new_line, arr_in)
					f.writelines(l1)
				else:
					for line in arr_in:
						f.write(line)
						f.write(new_line)
			except Exception as ex:
				print(f'Exception writelines', ex)
				pass
	f.close()


def dic_to_file(dic, path, rw='w', encoding='utf-8'):
	"""
	:param dic:
	:param path:
	:param rw:
	:param encoding:
	:return:
	"""
	# TODO refactoring - > dic_list_str_to_file_json
	text = ''
	for key, value in dic.items():
		key_str = '%s\n----' % key
		value_str = '\n----'.join(value) if isinstance(value, list) else '%s\n----' % value
		text += key_str + value_str
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with codecs.open(path, rw, encoding=encoding) as f:
		f.write(text)
	f.close()


def to_shelve(path, key, data):
	"""
	:param path:
	:param key:
	:param data:
	:return:
	"""
	with shelve.open(path) as db:
		db[str(key)] = data


def to_shelves(path, data):
	"""
	:param path:
	:param data:
	:return:
	"""
	with shelve.open(path) as db:
		for k, v in data.items():
			db[str(k)] = v


def from_shelve(path, key):
	"""
	:param path:
	:param key:
	:return:
	"""
	with shelve.open(path) as db:
		try:
			return db[key]
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			return {}


def str_filter_by_list(line, patterns):
	"""
	:param line:
	:param patterns:
	:return:
	"""
	if not isinstance(patterns, list):
		patterns = [patterns]
	if line:
		line = line.lower()
		for pattern in patterns:
			pattern = pattern.lower()
			find = line.find(pattern)
			if find >= 0:
				return True
	return False


def merge(path1: str, path2: str, result_dir: str):
	"""
	:param path1:
	:param path2:
	:param result_dir:
	:return:
	"""
	path1 = path1.replace('\\', '/')
	path2 = path2.replace('\\', '/')
	name1 = path1.rpartition('/')[2]
	name2 = path2.rpartition('/')[2]
	reder1 = read_big(path1)
	reder2 = read_big(path2)
	result1 = []
	result2 = []
	difs = 0
	while True:
		try:
			line1 = next(reder1)
			line2 = next(reder2)
		except Exception as ex:
			print(f'Exception', difs, ex)
			break
		if line1 == line2:
			continue
		result1.append(line1)
		result2.append(line2)
		difs += 1
		if len(result1) >= 1000:
			arr_to_file(result1, f'{result_dir}/{name1}', rw='ab', ext=None, encoding=None)
			arr_to_file(result2, f'{result_dir}/{name2}', rw='ab', ext=None, encoding=None)
			result1 = []
			result2 = []
	return difs
