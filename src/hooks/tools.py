import functools
import os
import random
import re
import shutil
import stat
import string
import time
from os import listdir
from os.path import isfile
from os.path import join as joinpath
from pathlib import Path
from typing import List, Union

import pkg_resources
from glob2 import iglob
from humanize import naturalsize, precisedelta

from ..config import log


def empty_function(*args, **kwargs):
	"""
	:param args:
	:param kwargs:
	:return:
	"""
	return args, kwargs


def path_split(path):
	"""
	:param path:
	:return:
	"""
	_list = path.split(os.path.sep)
	res = []
	for r in _list:
		if r != '':
			res.append(r)
	return res


def path_norm(path):
	"""
	:param path:
	:return:
	"""
	return os.path.normpath(path)


def path_dir(path):
	"""
	:param path:
	:return:
	"""
	return os.path.dirname(path)


def path_abs(path):
	"""
	:param path:
	:return:
	"""
	return os.path.abspath(path)


def path_join(*args):
	"""
	:param args:
	:return:
	"""
	return os.path.join(*args)


def copy_set(name, p1, p2):
	"""
	:param name:
	:param p1:
	:param p2:
	:return:
	"""
	return (
		path_join(p1, name),
		path_join(p2, name)
	)


def get_cwd_win(mod=None):
	"""
	:param mod:
	:return:
	"""
	s = str(get_cwd(mod))
	try:
		s = s.replace("\\", "/")
	except Exception as ex:
		log('Exception', ex)
	return s


def get_cwd(mod=None, *args):
	"""
	:param mod:
	:param args:
	:return:
	"""
	return path_join(path_dir(path_abs(mod or __file__)), *args)


def get_data(mod=None, path_dir_name='data', path_file='data.txt'):
	"""
	:param mod:
	:param path_dir_name:
	:param path_file:
	:return:
	"""
	_ROOT = get_cwd(mod)
	return path_join(_ROOT, path_dir_name, path_file)


def get_resource_path(name=None, path_dir_name='data', path_file='data.txt'):
	"""
	:param name:
	:param path_dir_name:
	:param path_file:
	:return:
	"""
	_data = path_join(path_dir_name, path_file)
	_ROOT = pkg_resources.resource_filename(name or __name__, _data)
	return path_abs(_ROOT)


def get_resource_data(name=None, path_dir_name='data', path_file='data.txt'):
	"""
	:param name:
	:param path_dir_name:
	:param path_file:
	:return:
	"""
	_data = path_join(path_dir_name, path_file)
	_ROOT = pkg_resources.resource_string(name or __name__, _data)
	return _ROOT


def get_size_dir_natural(path='.'):
	"""
	:param path:
	:return:
	"""
	return naturalsize(sum(os.path.getsize(x) for x in iglob(path)))


def get_size_dir_walk(path='.'):
	"""
	:param path:
	:return:
	"""
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(path):
		for f in filenames:
			fp = path_join(dirpath, f)
			total_size += os.path.getsize(fp)
	return total_size


def get_size_dir_scandir(path='.'):
	"""
	:param path:
	:return:
	"""
	total = 0
	for entry in os.scandir(path):
		if entry.is_file():
			total += entry.stat().st_size
		elif entry.is_dir():
			total += get_size_dir_scandir(entry.path)
	return total


def get_files_from_dir(path='.'):
	"""
	:param path:
	:return:
	"""
	r = [f.name for f in os.scandir(path) if f.is_file()]
	return r


def get_dirs_from_dir(path='.'):
	"""
	:param path:
	:return:
	"""
	r = [f.name for f in os.scandir(path) if f.is_dir()]
	return r


def file_list(path, ext=False):
	"""
	:param path:
	:param ext:
	:return:
	"""
	ls_dir = listdir(path=path)
	ls_dir.sort()
	out_list = [path + '/' + files for files in ls_dir if isfile(joinpath(path, files))]
	if ext:
		out_list = [file for file in out_list if file.endswith('.' + str(ext))]
	return out_list


def folder_reed_recrussive(path, ext='*'):
	"""
	:param path:
	:param ext:
	:return:
	"""
	path = os.path.normpath(path)
	res = {}
	for root, dirs, files in os.walk(path):
		data_files = []
		file_dir_full = os.path.normpath(root)
		file_dir = file_dir_full.replace(path, '')
		file_dir_list = path_split(file_dir)
		if not file_dir_list:
			file_dir_list = ['root']
		
		try:
			r = res[file_dir_list[0]]
		except Exception as _ex:
			r = {}
			res[file_dir_list[0]] = r
		for directory in file_dir_list[1:]:
			try:
				r = r[directory]
			except Exception as _ex:
				r[directory] = {}
				r = r[directory]
		
		for _file in files:
			file_name, _ext = os.path.splitext(_file)
			_ext = _ext[1:]
			if _ext == ext or ext == '*':
				file_path_full = os.path.join(root, _file)
				data_files.append((file_name, file_path_full))
				r[file_name] = file_path_full
	return res


def folder_reed_recrussive_glob(path, ext='*.*'):
	"""
	:param path:
	:param ext:
	:return:
	"""
	res = []
	for _file in iglob(path + '/**/%s' % ext, recursive=True):
		res.append(_file)
	return res


def folder_reed_recrussive_files(path: Union[List, str], ext=None):
	"""
	:param path:
	:param ext:
	:return:
	"""
	if not isinstance(path, list):
		path = [path]
	for _path in path:
		if Path(_path).is_file():
			yield _path
		for currentpath, folders, files in os.walk(_path):
			for file in files:
				file_name = os.path.join(currentpath, file)
				if ext is not None:
					if file_name.endswith(ext):
						yield file_name
					else:
						continue
				else:
					yield file_name


def move_file(path_from, path_to):
	"""
	:param path_from:
	:param path_to:
	:return:
	"""
	os.makedirs(os.path.dirname(path_to), exist_ok=True)
	shutil.move(path_from, path_to)


def is_dir(s):
	"""
	:param s:
	:return:
	"""
	try:
		return os.path.isdir(s)
	except Exception as ex:
		print(f'Exception = {ex}')
		return False


def copytree(src, dst, symlinks=False, ignore=None, dirs_exist_ok=True):
	"""
	Странная ошибка вылазит str not callable
	:param src:
	:param dst:
	:param symlinks:
	:param ignore:
	:param dirs_exist_ok:
	:return:
	"""
	os.makedirs(dst, exist_ok=True)
	_head, _tail = os.path.split(src)
	s = path_norm(src)
	d = path_norm(path_join(dst, _tail))
	if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
		if is_dir(src):
			shutil.copytree(s, d, symlinks, ignore, dirs_exist_ok=dirs_exist_ok)
		else:
			shutil.copy2(s, d)
	return None


def copytree_old(src, dst, symlinks=False, ignore=None):
	"""
	:param src:
	:param dst:
	:param symlinks:
	:param ignore:
	:return:
	"""
	if not os.path.exists(dst):
		os.makedirs(dst)
	for item in os.listdir(src):
		if item != '__pycache__':
			s = path_join(src, item)
			d = path_join(dst, item)
			if os.path.isdir(s):
				copytree(s, d, symlinks, ignore)
			else:
				if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
					shutil.copy2(s, d)
	return None


def copytree2(src, dst, symlinks=False, ignore=None):
	"""
	:param src:
	:param dst:
	:param symlinks:
	:param ignore:
	:return:
	"""
	if not os.path.exists(dst):
		os.makedirs(dst)
		shutil.copystat(src, dst)
	lst = os.listdir(src)
	if ignore:
		excl = ignore(src, lst)
		lst = [x for x in lst if x not in excl]
	for item in lst:
		s = path_join(src, item)
		d = path_join(dst, item)
		if symlinks and os.path.islink(s):
			if os.path.lexists(d):
				os.remove(d)
			os.symlink(os.readlink(s), d)
			try:
				st = os.lstat(s)
				mode = stat.S_IMODE(st.st_mode)
				os.lchmod(d, mode)
			except Exception as _ex:
				pass  # lchmod not available
		elif os.path.isdir(s):
			copytree2(s, d, symlinks, ignore)
		else:
			shutil.copy2(s, d)


def clear_folder_by_pattern(path, pattern='tmp[.]+'):
	"""
	
	:param path:
	:param pattern:
	:return:
	"""
	for file in os.scandir(path):
		if re.search(pattern, file.name):
			os.unlink(file.path)


def map_many(iterable, function, *othersfunctions):
	"""
	
	:param iterable:
	:param function:
	:param othersfunctions:
	:return:
	"""
	if othersfunctions:
		return map_many(map(function, iterable), *othersfunctions)
	return map(function, iterable)


def compose(*funcs):
	"""
	
	:param funcs:
	:return:
	"""
	return lambda x: functools.reduce(lambda v, f: f(v), reversed(funcs), x)


def password_generator(size=8, chars=string.ascii_letters + string.digits):
	"""
	:param size: default=8; override to provide smaller/larger passwords
	:param chars: default=A-Za-z0-9; override to provide more/less diversity
	:return:
	"""
	return ''.join(list(map(lambda i: random.choice(chars), range(size))))


def memoize(func):
	"""
	:param func:
	:return:
	"""
	cache = func.cache = {}
	
	@functools.wraps(func)
	def memoized_func(*args, **kwargs):
		key = str(args) + str(kwargs)
		if key not in cache:
			cache[key] = func(*args, **kwargs)
		return cache[key]
	
	return memoized_func


def sizeof_fmt(num, suffix='B'):
	"""
	:param num:
	:param suffix:
	:return:
	"""
	for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
		if abs(num) < 1024.0:
			return "%3.1f%s%s" % (num, unit, suffix)
		num /= 1024.0
	return "%.1f%s%s" % (num, 'Yi', suffix)


def get_file_size(path, readable=False):
	"""
	:param path:
	:param readable:
	:return:
	"""
	size = Path(path).stat().st_size
	return naturalsize(size) if readable else size


def _originalsize(x):
	return x


def reed_recursive(path: Union[List, str], readable=False):
	"""
	:param path:
	:param readable: naturalsize view
	:return: _i, _path, _count, _size, _total_size
	"""
	
	if readable:
		_view = naturalsize
	else:
		_view = _originalsize
	
	try:
		paths = list(folder_reed_recrussive_files(path))
		_count = len(paths)
		_path_sizes = [Path(x).stat().st_size for x in paths]
		_total_size = _view(sum(_path_sizes))
		for _i, _path in enumerate(paths):
			yield _i + 1, _path, _count, _view(_path_sizes[_i]), _total_size
	except Exception as ex:
		log(f'Exception', ex, level='warning')
		pass


def reed_recursive_with_log(path: Union[List, str], readable=False):
	"""
	:param path:
	:param readable:
	:return:
	"""
	start = now = time.time()
	done_size = 0
	done_files = 0
	for n, _path, _count, _size, _total_size in reed_recursive(path, readable):
		done_size += _size
		done_files += 1
		now, prev = time.time(), now
		done_prc = 100 * done_size / _total_size
		work_time = now - start
		left_time = ((100 / done_prc) * work_time) - work_time
		report = \
			f'File {n} of {_count} left {_count - n}, {naturalsize(_size)} in {naturalsize(done_size)} ' \
			f'{round(done_prc, 2)} %, last {precisedelta(now - prev)}, total {precisedelta(work_time)}, ' \
			f'left {precisedelta(left_time)}, {_path}'
		log(report)
		yield n, _path, _count, _size, _total_size


@memoize
def _buf_gen(size):
	"""
	:param size:
	:return:
	"""
	return size * size


def line_count_1(path):
	"""
	:param path:
	:return:
	"""
	with open(path, mode='rb', encoding=None) as f:
		lines = 0
		buf_size = _buf_gen(1024)
		read_f = f.read  # loop optimization
		buf = read_f(buf_size)
		while buf:
			lines += buf.count(b'\n')
			buf = read_f(buf_size)
		return lines


lines_in_file = line_count_1
