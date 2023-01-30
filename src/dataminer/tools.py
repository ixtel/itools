import itertools
import json
import math
from collections import OrderedDict
from itertools import zip_longest
from random import randint

import numpy as np
import pandas as pd
from toolz.itertoolz import partition_all

from ..config import log


def data_req_load(req, def_val=''):
	"""
	:param req:
	:param def_val:
	:return:
	"""
	if not isinstance(req, str):
		req = json.dumps(req)
	if req:
		data = json.loads(req)
		return data
	else:
		return def_val


def data_req_dump(data=False, key='response', def_val=''):
	"""
	:param data:
	:param key:
	:param def_val:
	:return:
	"""
	res = data if data else def_val
	return json.dumps({key: res})


def chunker_dict(dic, n):
	"""
	# d = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}
	:param dic:
	:param n:
	:return:
	"""
	chunks = [iter(dic.items())] * n
	g = (dict(filter(None, v)) for v in zip_longest(*chunks))
	return list(g)


def chunker_arr(arr, n=25):
	"""
	# list => [(X) lists by N item per list]
	:param arr:
	:param n:
	:return:
	"""
	chunks = partition_all(n, arr)
	return [list(c) for c in chunks if c]


def maper(arr, n):
	"""
	# list => [N lists by (X) item per list]
	:param arr:
	:param n:
	:return:
	"""
	chunks = np.array_split(arr, n)
	return [list(c) for c in chunks if len(c)]


def ordic(obj):
	"""
	:param obj:
	:return:
	"""
	return OrderedDict(sorted(obj.items(), key=lambda x: x, reverse=False))


def ordic_v(obj, reverse=False):
	"""
	:param obj:
	:param reverse:
	:return:
	"""
	return OrderedDict(sorted(obj.items(), key=lambda x: x[1], reverse=reverse))


def ordic_val_len(obj):
	"""
	:param obj:
	:return:
	"""
	return OrderedDict(sorted(obj.items(), key=lambda x: len(x[1]), reverse=True))


def merge_lists(lst1, lst2, savesorted=False):
	"""
	if savesorted:
		# добавление недостающих элементов из второго в первый
		# сохраняя порядок первого
	else:
		# Слияние листов. только уникальные элементы
		# без сохранения порядка
	:param lst1:
	:param lst2:
	:param savesorted:
	:return:
	"""
	if savesorted:
		for i in lst2:
			if i not in lst1:
				lst1.append(i)
		return lst1
	else:
		return list(set(lst1 + lst2))


def compare_list(lst1, lst2):
	"""
	# пересечения. элементы которые есть в обоих листах
	:param lst1:
	:param lst2:
	:return:
	"""
	lst1 = set(lst1)
	lst2 = set(lst2)
	lst3 = list(lst1 & lst2)
	lst3.sort()
	return lst3


def extract_lists(items):
	"""
	:param items:
	:return:
	"""
	flattened = []
	for i in items:
		if isinstance(i, list):
			i_flattened = extract_lists(i)
			flattened += i_flattened
		else:
			flattened.append(i)
	return flattened


def nested_list_flatten(container):
	"""
	:param container:
	:return:
	"""
	for i in container:
		if isinstance(i, (list, tuple)):
			for j in nested_list_flatten(i):
				yield j
		else:
			yield i


def fnum(k, size=15000):
	"""
	:param k:
	:param size:
	:return:
	"""
	return math.floor(int(k) / size)


def to_map(dictionary):
	"""
	:param dictionary:
	:return:
	"""
	res = {}
	for k in dictionary:
		res[fnum(k)][k] = pd.Series(dictionary[k])
	return res


def map_hdf_set(table, res, append=True, f='table'):
	"""
	:param table:
	:param res:
	:param append:
	:param f:
	:return:
	"""
	if append is False:
		f = 'fixed'
	for num, vals in res.items():
		with pd.HDFStore('./hdfs/{}/{}.h5'.format(table, num)) as hdf:
			for k, data in vals.items():
				data.to_hdf(hdf, k, format=f, append=append, complib='blosc')


def chunks_gen_free(_min, _max, count, leght):
	"""
	:param _min:
	:param _max:
	:param count:
	:param leght:
	:return:
	"""
	time_run = []
	time_sum = 0
	for i in range(count):
		p = randint(_min, _max)
		time_run.append(p)
		time_sum += p
	log('time_sum %s', time_sum)
	log('leght %s', leght)
	return time_run


def chunks_gen(_min, _max, count, leght):
	"""
	:param _min:
	:param _max:
	:param count:
	:param leght:
	:return:
	"""
	time_run = []
	time_sum = 0
	# создаем список стартов
	for i in range(count):
		p = randint(_min, _max)
		time_run.append(p)
		time_sum += p
	# на сколько сумма визитов больше
	time_over = leght - time_sum
	time_sleep = [0] * count
	time_sleep_sum = 0
	# Если сумма визитов меньше выделенного времени
	if time_sum < leght:
		# пока сумма пауз между визитами меньше "перерасхода"
		while time_sleep_sum < time_over:
			# берем случайный визит
			n = randint(0, count - 1)
			# и прибавляем к нему секунду задержки
			time_sleep[n] += 1
			time_sleep_sum += 1
	# Если сумма визитов больше выделенного времени
	elif time_sum > leght:
		# минимальное время захода
		# пока "перерасход" меньше нуля
		while time_over < 0:
			# берем случайный визит
			_count = len(time_run)
			n = randint(0, _count - 1)
			# и прибавляем к нему секунду задержки
			# если время визита больше минимального
			if time_run[n] > _min:
				# вычитаем секунду из визита
				time_run[n] -= 1
				time_over += 1
			# если в списке остались только визиты с минимальным временем,
			if max(time_run) == _min:
				# удаляем случайны
				time_run.pop(n)
				time_sleep.pop(n)
				time_over += _min
	return time_run, time_sleep


def keywords_maper(keywords):
	"""
	:param keywords:
	:return:
	"""
	r = []
	for key, count in keywords.items():
		for c in range(int(count)):
			r.append(str(key))
	return r


def keywords_list_to_dic(keywords):
	"""
	:param keywords:
	:return:
	"""
	result = {}
	for iteml in keywords:
		result[iteml['keyword']] = iteml['count']
	return result


def extract_dict(dictionary, name=None):
	"""
	:param dictionary:
	:param name:
	:return:
	"""
	result = []
	for k, v in dictionary.items():
		v = int(v)
		if v > 0:
			for i in range(1, v + 1):
				if name:
					result.append({name: k})
				else:
					result.append(k)
	return result


def lict_compres_dict(items, key='_key'):
	"""
	:param items:
	:param key:
	:return:
	"""
	result = {item[key]: item for item in items}
	return result


def merge_list_dicts(l1, l2):
	"""
	:param l1:
	:param l2:
	:return:
	"""
	result = []
	for i, r in enumerate(l1):
		r.update(l2[i])
		result.append(r)
	return result


def df_grouping(df, col_group):
	"""
	:param df:
	:param col_group:
	:return:
	"""
	grouping = df.groupby(col_group)
	grouping = sorted(
		grouping,  # iterates pairs of (key, corresponding subDataFrame)
		key=lambda x: len(x[1]),  # sort by number of rows (len of subDataFrame)
		reverse=True
	)
	return grouping


def df_grouping_count(df, col_group):
	"""
	:param df:
	:param col_group:
	:return:
	"""
	grouping = df.groupby(col_group).size()
	return grouping


def df_grouping_count_calc(df, col_group, col_data, calc_field='count'):
	"""
	:param df:
	:param col_group:
	:param col_data:
	:param calc_field:
	:return:
	"""
	index = list(set(list(df[col_group])))
	counts = df.groupby(col_group)  # , sort=True)
	matrix = pd.DataFrame(counts.size()).reset_index()
	matrix.columns = [col_group, calc_field]
	matrix[calc_field] = matrix[calc_field].astype(int)
	matrix.set_index([col_group], inplace=1)
	counts = pd.DataFrame(pd.Series(counts.groups)).reset_index()
	counts.columns = [col_group, col_data]
	counts.set_index([col_group], inplace=1)
	return index, counts, matrix


def get_dic_traverse_action(d, callback):
	"""
	:param d:
	:param callback:
	:return:
	"""
	res = {}
	for k, v in d.items():
		if isinstance(v, dict):
			value = get_dic_traverse_action(v, callback)
		else:
			value = callback(v)
		res[k] = value
	return res


def product_dict(dic):
	"""
	:param dic:
	:return:
	"""
	keys = dic.keys()
	vals = dic.values()
	res = []
	for instance in itertools.product(*vals):
		_r = dict(zip(keys, instance))
		res.append(_r)
	return res


def product_dicts(dicts):
	"""
	>>> list(product_dicts(dict(number=[1,2], character='ab')))
	[
		{'character': 'a', 'number': 1},
		{'character': 'a', 'number': 2},
		{'character': 'b', 'number': 1},
		{'character': 'b', 'number': 2}
	]
	:param dicts:
	:return:
	"""
	return (dict(zip(dicts, x)) for x in itertools.product(*dicts.values()))


def dic_traverse_unpack(obj):
	"""
	:param obj:
	:return:
	"""
	if isinstance(obj, (str, int, float)):
		return obj
	if isinstance(obj, (list, set, tuple)):
		obj_res = obj.__class__(dic_traverse_unpack(v) for i, v in enumerate(obj))
		return obj_res
	elif isinstance(obj, dict):
		obj_res = obj.__class__()
		for k, v in obj.items():
			obj_res[k] = dic_traverse_unpack(v)
		return obj_res
	else:
		return obj


def dic_traverse_value_handler(data, handler=None, handler_arg=None):
	"""
	:param data:
	:param handler:
	:param handler_arg:
	:return:
	"""
	_res = data
	if isinstance(data, (list, set)):
		_res = []
		for _d in data:
			_dr = dic_traverse_value_handler(_d, handler, handler_arg)
			_res.append(_dr)
		return _res
	elif isinstance(data, dict):
		_res = {}
		for k, v in data.items():
			vr = dic_traverse_value_handler(v, handler, handler_arg)
			_res[k] = vr
		return _res
	else:
		if handler:
			_res = handler(data, handler_arg)
			return _res
		else:
			return data


def log_dic_key(obj, handler=None, traverse=False, inlist=False):
	"""
	:param obj:
	:param handler:
	:param traverse:
	:param inlist:
	:return:
	"""
	if isinstance(obj, dict):
		for k, v in obj.items():
			if handler:
				handler(k, v)
			if traverse:
				log_dic_key(v)
	elif isinstance(obj, (list, set, tuple)) and inlist:
		for i, v in enumerate(obj):
			if handler:
				handler(i, v)
			if traverse:
				log_dic_key(v)
