import itertools
import math
from decimal import Decimal
from typing import List

from ..config import log


def product_str(numbers, length, n, offsets, start=0, count=10 ** 5):
	"""
	:param numbers:
	:param length:
	:param n:
	:param offsets:
	:param start:
	:param count:
	:return:
	"""
	for row in range(start, start + count):
		p = ''
		for col in range(length):
			p += numbers[int((row // offsets[col]) % n)]
		yield p


def product_with_prebuild(numbers: List[str], length: int, n: int, offsets: List[int], start=0, count=10 ** 5) -> str:
	"""
	:param numbers: alphabet list
	:param length: len result variant
	:param n: len alphabet list
	:param offsets: list(n ** col)
	:param start: start position
	:param count: count generate
	:return:
	"""
	stop = start + count
	for row in range(start, stop):
		p = []
		for col in range(length):
			r = numbers[int((row // offsets[col]) % n)]
			p.append(r)
		yield ''.join(p)


def product_pure_horizontal(numbers, length, start=0, count=None):
	"""
	:param numbers:
	:param length:
	:param start:
	:param count:
	:return:
	"""
	n = len(numbers)
	permutations = (n ** length)
	
	if count is None:
		stop = permutations
	else:
		stop = start + count
	
	offsets = []
	for col in range(length):
		offsets.append(n ** col)
	
	for row in range(start, stop):
		p = []
		for col in range(length):
			r = numbers[int((row // offsets[col]) % n)]
			p.append(r)
		yield ''.join(p)


def unique_everseen_v0(iterable, key=None, agg=None):
	"""
	:param iterable:
	:param key:
	:param agg:
	:return:
	"""
	seen = set()
	seen_add = seen.add
	if agg is None:
		print('agg is None')
		for element in itertools.filterfalse(seen.__contains__, iterable):
			print('element', element)
			if key is not None:
				print('element1', element)
				element = element[key]
				print('element2', element)
			seen_add(element)
			yield element
	else:
		for element in iterable:
			element = agg(element)
			if element not in seen:
				seen_add(element)
				yield element


def unique_everseen(iterable, key=None, agg=None):
	"""
	:param iterable:
	:param key:
	:param agg:
	:return:
	"""
	seen = set()
	seen_add = seen.add
	for element in iterable:
		if key is not None:
			element = element[key]
		if agg is not None:
			element = agg(element)
		if element not in seen:
			seen_add(element)
			yield element


def grouper(iterable, n, fillvalue=None):
	"""
	сжимает список в список списков по n штук
	[1 ,2 ,3, 4 ,5, 6] => [[1, 2][3, 4][5, 6]]
	:param iterable:
	:param n:
	:param fillvalue:
	:return:
	"""
	args = [iter(iterable)] * n
	return list(itertools.zip_longest(*args, fillvalue=fillvalue))


def ungrouper(iterable):
	"""
	расжимает список списков в один список
	[[1, 2][3, 4][5, 6]] = > [1 ,2 ,3, 4 ,5, 6]
	:param iterable:
	:return:
	"""
	return list(itertools.chain(*iterable))


def permutator(items: list, length_from: int = 1, length_to: int = 1) -> list:
	"""
	:param items:
	:param length_from:
	:param length_to:
	:return:
	"""
	n = length_to if length_to > 1 else len(items)
	for i in range(length_from, n + 1):
		for instance in itertools.permutations(items, r=i):
			_r = ''.join(list(instance))
			yield _r
	pass


def range_prod(lo, hi):
	"""
	:param lo:
	:param hi:
	:return:
	"""
	if lo + 1 < hi:
		mid = (hi + lo) // 2
		return range_prod(lo, mid) * range_prod(mid + 1, hi)
	if lo == hi:
		return lo
	return lo * hi


def treefactorial(n):
	"""
	:param n:
	:return:
	"""
	if n < 2:
		return 1
	return range_prod(1, n)


def productor(items: list, length_from: int = 1, length_to: int = 1) -> list:
	"""
	Перестановки(Размщения) в заданном диапазоне без повторений в цикле,
	если длинна больше числа массивов сочетания получаются из массива уровнем ниже.
	:param items: список списков [[aple banana orange][1 2]] => [apple1 apple2 banana1 banana2 orange1 orange1]
	:param length_from:
	:param length_to:
	:return: generator
	"""
	n = length_to if length_to >= 0 else len(items)
	for i in range(length_from, n + 1):
		for instance in itertools.product(*items, repeat=i):
			yield instance
	pass


def combinator(items: list, n: int = 1) -> list:
	"""
	в комбинациях порядок элементов не важен 1f# == f1#
	:param items: массив элементов
	:param n: длинна перестановок
	:return: generator
	"""
	n = n if n >= 0 else len(items) + 1
	for i in range(1, n):
		for instance in itertools.combinations_with_replacement(items, i):
			yield instance
	pass


def permutator_calc(n: int = 3, k: int = 3) -> int:
	"""
	Вычисление количества перестанововк
	:param k: длинна варианта
	:param n: всего элементов в исходном списке
	:return:
	"""
	if n == k:
		result = treefactorial(n)
	else:
		result = treefactorial(n) / treefactorial(n - k)
	return result


def permutator_az(alphabet: list, k: int, length_all=False, parent=''):
	"""
	:param alphabet:
	:param k:
	:param length_all:
	:param parent:
	:return:
	"""
	if k > 0:
		for e in alphabet:
			if k > 1:
				for i in permutator_az(alphabet=alphabet, k=k - 1, length_all=length_all, parent=parent + e):
					yield i
				else:
					if length_all:
						yield parent + e
			else:
				_r = parent + e
				yield _r


def permutator_az_calc(k=3, n=3):
	"""
	:param k:
	:param n:
	:return:
	"""
	variants = math.factorial(n) / math.factorial(n - k)
	combinats = n ** k
	log('сочетаний', variants, 'размещения', combinats)
	return variants, combinats


def file_size_calc(k: int = 3, n: int = 3) -> int:
	"""
	Вычисление размера файла из количества строк и длинны
	:param k: количество строк
	:param n: длинна строки
	:return:
	"""
	result = k * (n + 1)
	return result


def permutattor_calc_file(length_from=1, length=5):
	"""
	:param length_from:
	:param length:
	:return:
	"""
	print('length_from ==', length_from, 'length ==', length)
	lines_count = 0
	file_size = 0
	for i in range(length_from, length + 1):
		_lines_count = permutator_calc(length, i)
		_file_size = file_size_calc(_lines_count, i)
		lines_count += _lines_count
		file_size += _file_size
	file_size_d = Decimal(file_size)
	print('Lines count', lines_count)
	print('File size byte', file_size_d)
	print('File size Kb', file_size_d / 1000)
	print('File size Mb', file_size_d / 1000000)
	print('File size Gb', file_size_d / 1000000000)
	print('File size Tb', file_size_d / 1000000000000)
	return lines_count, file_size_d
