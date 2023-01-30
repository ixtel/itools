import subprocess
import winreg

from ..config import log
from .tools import get_size_dir_scandir


def get_env(system=False, variable='TEMP'):
	"""
	:param system:
	:param variable: 'TEMP'
	:return:
	"""
	if system:
		reg_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
		reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
	else:
		reg_path = r'Environment'
		reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
	try:
		return winreg.ExpandEnvironmentStrings(winreg.QueryValueEx(reg_key, variable)[0])
	except Exception as ex:
		log('Exception', ex)
		return None


def temp_check(max_size_gb):
	"""
	:param max_size_gb:
	:return:
	"""
	try:
		paths = temp_get()
		for path in paths:
			if path is not None:
				temp_calc(path, max_size_gb)
	except Exception as ex:
		log('Exception', ex)
	return None


def temp_get():
	"""
	:return:
	"""
	paths = []
	try:
		paths.append(get_env(True))
	except Exception as ex:
		log('Exception', ex)
	try:
		paths.append(get_env(False))
	except Exception as ex:
		log('Exception', ex)
	return paths


def temp_calc(folder, max_size_gb=1):
	"""
	:param folder:
	:param max_size_gb:
	:return:
	"""
	max_size_gb = float(max_size_gb)
	max_size_bytes = max_size_gb * 1024 * 1024 * 1024
	try:
		cur_size = get_size_dir_scandir(folder)
		if int(cur_size) > int(max_size_bytes):
			log('OverSize', int(cur_size) - int(max_size_bytes))
			temp_clear(folder)
	except Exception as ex:
		log('Exception', ex)


def temp_clear(path):
	"""
	:param path:
	:return:
	"""
	pattern = '*'
	cmd = 'forfiles.exe /P {0} /S /M {1} /D -0 /C "cmd /C rd /S /Q @file"'.format(path, pattern)
	try:
		subprocess.Popen(cmd)
	except Exception as ex:
		log('Exception', ex)
