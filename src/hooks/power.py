import ctypes
from threading import Timer

from ..rewr.tools import text_to_file, file_to_text
# noinspection PyPackageRequirements
import win32api
# noinspection PyPackageRequirements
import win32security

from ..config import log


def suspend(hibernate=False):
	"""Puts Windows to Suspend/Sleep/Standby or Hibernate.

	Parameters
	----------
	hibernate: bool, default False
		If False (default), system will enter Suspend/Sleep/Standby state.
		If True, system will Hibernate, but only if Hibernate is enabled in the
		system settings. If it's not, system will Sleep.

	--------
	>>> suspend()
	# Enable the SeShutdown privilege (which must be present in your
	# token in the first place)
	"""
	priv_flags = (win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY)
	h_token = win32security.OpenProcessToken(
		win32api.GetCurrentProcess(),
		priv_flags
	)
	priv_id = win32security.LookupPrivilegeValue(
		None,
		win32security.SE_SHUTDOWN_NAME
	)
	old_privs = win32security.AdjustTokenPrivileges(
		h_token,
		0,
		[(priv_id, win32security.SE_PRIVILEGE_ENABLED)]
	)
	
	if win32api.GetPwrCapabilities()['HiberFilePresent'] is False and hibernate is True:
		import warnings
		warnings.warn("Hibernate isn't available. Suspending.")
	try:
		ctypes.windll.powrprof.SetSuspendState(hibernate, True, False)
	except Exception as ex:
		log(f'Exception', ex, level='warning')
		win32api.SetSystemPowerState(not hibernate, True)
	
	# Restore previous privileges
	win32security.AdjustTokenPrivileges(
		h_token,
		0,
		old_privs
	)
	return True


HANDLERS = dict(
	hibernate=lambda: suspend(True),
	suspend=suspend,
)

HANDLERS_ON_DONE = [
	'hibernate'
]


def set_timeout(func, delay=10, *args, **kwargs):
	"""
	:param func:
	:param delay:
	:param args:
	:param kwargs:
	:return:
	"""
	timer = Timer(delay, func, args, kwargs)
	timer.start()
	return 'ok'


def handlers_on_done(handlers=None):
	"""
	:param handlers:
	:return:
	"""
	if handlers is None:
		handlers = HANDLERS_ON_DONE
	
	for handler_name in handlers:
		log('handler on done', handler_name)
		handler = HANDLERS.get(handler_name)
		if handler is not None:
			result = set_timeout(handler)
			log('handler on done result', result)
	return


def file_flag_set(path='./flag_hibernate.txt', value=0):
	"""
	:param path:
	:param value:
	:return:
	"""
	text_to_file(str(value), path)
	return


def file_flag_get(path='./flag_hibernate.txt', value=0):
	"""
	:param path:
	:param value:
	:return:
	"""
	flag = file_to_text(path)
	try:
		flag_int = int(flag)
	except Exception as ex:
		log(f'Exception', ex, level='warning')
		return value
	return flag_int


def suspend_from_flag():
	"""
	:return:
	"""
	flag_int = file_flag_get('./flag_hibernate.txt')
	if flag_int == 1:
		suspend()
	elif flag_int == 2:
		suspend(True)
	else:
		pass
	
	return
