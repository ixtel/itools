import os
import signal
import subprocess
import time
from typing import Union

import psutil

from ..config import log


def out_of_memory():
	"""
	:return:
	"""
	try:
		_memory = psutil.virtual_memory()
		if _memory.percent > 80.0:
			return True
	except Exception as ex:
		log(f'Exception', ex, level='warning')
		return True
		pass
	return False


def over_of_memory_process(pid, limit=1.5):
	"""
	:param pid:
	:param limit:
	:return:
	"""
	try:
		process = psutil.Process(pid)
		_memory = process.memory_info().vms / 1024 ** 3
		if _memory > limit:
			return True
	except Exception as ex:
		log(f'Exception', ex, level='warning')
		return False
	return False


def kill_process_tskm(pids: Union[str, int, list]):
	"""
	:param pids:
	:return:
	"""
	if isinstance(pids, str) or isinstance(pids, int):
		try:
			subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=int(pids)))
		except Exception as ex:
			print(ex)
	elif isinstance(pids, list):
		for pid in pids:
			try:
				subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=int(pid)))
			except Exception as ex:
				print(ex)
	else:
		raise Exception('Bad format data')


def kill_process_os(pid):
	"""
	:param pid:
	:return:
	"""
	try:
		os.killpg(os.getpgid(pid), signal.SIGTERM)
	except Exception as ex:
		log('Exception', ex)
		return None


def kill_process_with_children(pid):
	"""
	:param pid:
	:return:
	"""
	try:
		process = psutil.Process(pid)
	except Exception as _ex:
		process = None
	try:
		child_process = process.children(recursive=True)
	except Exception as _ex:
		child_process = None
	if child_process:
		for child in child_process:
			try:
				child.kill()
			except Exception as ex:
				log(ex)
	try:
		process.kill()
	except Exception as ex:
		log(ex)


def kill_process_firefox_with_parent(process, timeout):
	"""
	:param process:
	:param timeout:
	:return:
	"""
	try:
		executed = int(time.time()) - int(process.create_time())
		delta = executed - timeout
	except Exception as ex:
		log(ex)
		delta = 0
	try:
		parent = psutil.Process(process.ppid())
		process_pid = process.pid
	except Exception as _ex:
		parent = None
		process_pid = None
	try:
		parent_pid = parent.pid
	except Exception as _ex:
		parent_pid = None
	if parent_pid:
		if delta > 0:
			kill_process_with_children(process_pid)
			kill_process_with_children(parent_pid)
	else:
		kill_process_with_children(process_pid)


def _check_process_time(process_pid, process_time, timeout):
	"""
	:param process_pid:
	:param process_time:
	:param timeout:
	:return:
	"""
	log('time.time()', time.time())
	log('process_time', process_time)
	log('timeout', timeout)
	if over_of_memory_process(process_pid) or process_time and int(time.time()) - int(process_time) - int(timeout) > 0 or out_of_memory():
		log('kill', process_pid)
		kill_process_with_children(process_pid)


def kill_process_firefox(process, timeout):
	"""
	:param process:
	:param timeout:
	:return:
	"""
	try:
		process_time = process.create_time()
		process_pid = process.pid
	except Exception as ex:
		log('Exception', ex)
		process_time = None
		process_pid = None
	
	try:
		parent = psutil.Process(process.ppid())
		parent_pid = parent.pid
	except Exception as ex:
		log('Exception', ex)
		parent_pid = None
	
	if parent_pid:
		_check_process_time(process_pid, process_time, timeout)
	else:
		log('kill nohave parent', process_pid)
		kill_process_with_children(process_pid)


def kill_process_others_with_parent_ff(process):
	"""
	:param process:
	:return:
	"""
	try:
		process_pid = process.pid
	except Exception as _ex:
		process_pid = None
	
	try:
		parent = psutil.Process(process.ppid())
		parent_pid = parent.pid()
		parent_name = parent.name()
	except Exception as _ex:
		parent_pid = None
		parent_name = None
	
	if parent_pid and parent_name == 'firefox.exe':
		kill_process_with_children(process_pid)
		kill_process_with_children(parent_pid)
	else:
		kill_process_with_children(process_pid)


def kill_process_firefox_zombies(with_parent=False, process_path='robot', timeout=10 * 60):
	"""
	:param with_parent:
	:param process_path:
	:param timeout:
	:return:
	"""
	try:
		pids = psutil.pids()
		if pids:
			for pid in pids:
				try:
					process = psutil.Process(pid)
					process_name = process.name()
					process_exe = process.exe()
				except Exception as _ex:
					process = None
					process_name = None
					process_exe = None
				if process and process_name == 'firefox.exe' and process_path.lower() in process_exe.lower():
					if with_parent:
						log('kill with_parent')
						kill_process_firefox_with_parent(process, timeout)
					else:
						kill_process_firefox(process, timeout)
				elif process and process_name == 'WerFault.exe':
					kill_process_others_with_parent_ff(process)
				elif process and process_name == 'helper.exe':
					kill_process_others_with_parent_ff(process)
	except Exception as ex:
		log('Exception', ex)
		return None


def kill_process_robot_zombies(ps_name='python.exe', ps_filter='runer.py', timeout=10 * 60):
	"""
	:param ps_name:
	:param ps_filter:
	:param timeout:
	:return:
	"""
	try:
		pids = psutil.pids()
		if pids:
			for pid in pids:
				try:
					process = psutil.Process(pid)
					process_name = process.name()
					process_time = process.create_time()
					process_cmdline = process.cmdline()
				except Exception as _ex:
					continue
				if process and process_name == ps_name and ps_filter in process_cmdline[1].lower():
					_check_process_time(pid, process_time, timeout)
		return None
	except Exception as ex:
		log('Exception', ex)
		return None


def process_robot_count(ps_name='python.exe', ps_filter='runer.py'):
	"""
	:param ps_name: python.exe
	:param ps_filter: runer.py
	:return:
	"""
	try:
		return len(process_robot_list(ps_name, ps_filter))
	except Exception as ex:
		log('Exception', ex, level='critical')
		return 0


def process_robot_list(ps_name='python.exe', ps_filter='runer.py'):
	"""
	:param ps_name: python.exe
	:param ps_filter: runer.py
	:return:
	"""
	pids = list(psutil.pids())
	procs = []
	for pid in pids:
		try:
			process = psutil.Process(pid)
		except Exception as _ex:
			continue
		try:
			process_name = str(process.name())
			process_cmdline = process.cmdline()
		except Exception as _ex:
			continue
		try:
			if process_name.find(ps_name) > -1:
				if len(process_cmdline) >= 3:
					if process_name == ps_name and ps_filter in process_cmdline[1]:
						print('HAVE', process_name, process_cmdline)
						procs.append(pid)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
	
	return list(set(procs))


def process_firefox_count(process_path='robot'):
	"""
	:param process_path: 'robot'
	:return:
	"""
	try:
		return len(process_firefox_list(process_path))
	except Exception as ex:
		log('Exception', ex)
		return None


def process_firefox_list(process_path='robot'):
	"""
	:param process_path: 'robot'
	:return:
	"""
	procs = []
	pids = psutil.pids()
	for pid in pids:
		try:
			process = psutil.Process(pid)
		except Exception as _ex:
			process = None
		
		try:
			process_name = process.name()
			process_exe = process.exe()
		except Exception as _ex:
			process_name = None
			process_exe = None
		
		if process_name == 'firefox.exe' and process_path.lower() in process_exe.lower():
			try:
				parent = psutil.Process(process.ppid())
				parent_pid = parent.pid
				parent_name = parent.name()
			except Exception as _ex:
				parent_name = None
				parent_pid = None
			try:
				trig = (parent_name == 'python.exe')
			except Exception as _ex:
				trig = None
			if trig and parent_pid:
				procs.append(parent_pid)
	return list(set(procs))
