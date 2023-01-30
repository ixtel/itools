import math
import random
from functools import reduce
from random import choice

import numpy as np
from deprecated import deprecated

from .tools import ordic_v
from ..config import log


@deprecated(reason="not use delta")
def chart_log_new(size, count, delta_to_end=False):
	"""
	:param size:
	:param count:
	:param delta_to_end:
	:return:
	"""
	r = []
	items = [math.log(i, size + 1) + 1 for i in range(1, size + 1)]
	s = sum(items)
	for i in items:
		v = i * count / s
		r.append(max(int(v), 1))
	if delta_to_end is False:
		r.reverse()
	return r


def chart_log(size, count, _delta=1, delta_to_end=False):
	"""
	:param size:
	:param count:
	:param _delta:
	:param delta_to_end:
	:return:
	"""
	return chart_log_new(size, count, delta_to_end)


def list_norm_new(items, count):
	"""
	:param items:
	:param count:
	:return:
	"""
	r = []
	s = sum(items)
	for i in items:
		v = i * count / s
		r.append(int(v))
	return r


@deprecated(reason='not use size')
def list_norm(items, _size, count):
	"""
	:param items:
	:param _size:
	:param count:
	:return:
	"""
	return list_norm_new(items, count)


def list_adapte(items, count):
	"""
	:param items:
	:param count:
	:return:
	"""
	_items = list_norm(items)
	if sum(_items) - count > count / 10:
		list_adapte(_items, count)
	return _items


def prc_dict(dictionary, nums):
	"""
	:param dictionary:
	:param nums:
	:return:
	"""
	r = {}
	d = prc_norm(dictionary)
	nn = 0
	for k, v in d.items():
		n = int(nums / 100 * v)
		r[k] = n
		nn += n
	dif = nums - nn
	k = choice(list(r))
	r[k] += dif
	return r


def not_null(d):
	"""
	:param d:
	:return:
	"""
	r = {}
	for k, v in d.items():
		if v != 0:
			r[k] = v
	try:
		k = choice(list(r))
	except Exception as _ex:
		k = False
	return k


def prc_not_null(dictionary, count):
	"""
	:param dictionary:
	:param count:
	:return:
	"""
	r = {}
	nn = 0
	for k, v in dictionary.items():
		n = math.ceil(count / 100 * v)
		r[k] = n
		nn += n
	dif = count - nn
	if dif > 0:
		keys = ordic_v(r, False)
		while dif > 0:
			for k in keys:
				r[k] += 1
				dif -= 1
				if dif == 0:
					break
	if dif < 0:
		keys = ordic_v(r, True)
		while dif < 0:
			for k in keys:
				if r[k] > 0:
					r[k] -= 1
					dif += 1
				if dif == 0:
					break
	return r


def prc_norm(dictionary):
	"""
	:param dictionary:
	:return:
	"""
	r = {}
	s = sum(dictionary.values())
	for k, v in dictionary.items():
		r[k] = int(v * 100 / s)
	return r


def line_sum(line):
	"""
	:param line:
	:return:
	"""
	s = 0
	for char in line:
		s += char
	return s


def prc_period(period, start, prc, operator):
	"""
	:param period:
	:param start:
	:param prc:
	:param operator:
	:return:
	"""
	if operator:
		r = reduce(lambda a, x: a + (a / 100) * prc, range(int(period)), start)
	else:
		r = reduce(lambda a, x: a - (a / 100) * prc, range(int(period)), start)
	return r


def abs_period(period, start, delta, operator):
	"""
	:param period:
	:param start:
	:param delta:
	:param operator:
	:return:
	"""
	if operator:
		r = reduce(lambda a, x: a + delta, range(int(period)), start)
	else:
		r = reduce(lambda a, x: a - delta, range(int(period)), start)
	return r


def list_balanced_rnd(items, count):
	"""
	:param items:
	:param count:
	:return:
	"""
	c_sum = sum(items)
	if c_sum > count:
		dif = c_sum - count
		while dif > 0:
			i = random.randint(0, len(items) - 1)
			e = items[i]
			e -= 1
			dif -= 1
			items[i] = e
	elif c_sum < count:
		dif = count - c_sum
		while dif > 0:
			i = random.randint(0, len(items) - 1)
			e = items[i]
			e += 1
			dif -= 1
			items[i] = e
	return items


def dict_balanced_rnd(items, count):
	"""
	:param items:
	:param count:
	:return:
	"""
	c_sum = sum(items.values())
	if c_sum > count:
		dif = c_sum - count
		while dif > 0:
			_l = {k: v for k, v in items.items() if v > 0}
			i = choice(list(_l.keys()))
			e = items[i]
			e -= 1
			dif -= 1
			items[i] = e
	elif c_sum < count:
		dif = count - c_sum
		while dif > 0:
			i = choice(list(items.keys()))
			e = items[i]
			e += 1
			dif -= 1
			items[i] = e
	return items


def _chunks_list(items, n):
	"""
	:param items:
	:param n:
	:return:
	"""
	r = []
	for i in range(0, len(items), n):
		r.append(items[i:i + n])
	return r


def chunk_count_to_list(n, count):
	"""
	:param n:
	:param count:
	:return:
	"""
	vec = 1 if n > 0 else -1
	n = abs(n)
	d = math.trunc(n / count)
	dd = math.fmod(n, count)
	items = []
	for i in range(d):
		items.append(count * vec)
	if dd != 0:
		items.append(int(dd * vec))
	return items


def _chunks_num(n, count):
	"""
	:param n:
	:param count:
	:return:
	"""
	# TODO BUG fix check
	d = math.trunc(n / count)
	dd = math.fmod(n, count)
	items = []
	for i in range(count):
		items.append(d)
	items.append(dd)  # !!!!!
	return d


def cumsum_sma(array, period):
	"""
	:param array:
	:param period:
	:return:
	"""
	array = np.array(array)
	ret = np.cumsum(array, dtype=float)
	ret[period:] = ret[period:] - ret[:-period]
	return ret[period - 1:] / period


def random_triger_with_desp(desp):
	"""
	:param desp:
	:return:
	"""
	try:
		_r = random.random() < desp
		return _r
	except Exception as ex:
		log(f'Exception', ex, level='warning')
		return True
