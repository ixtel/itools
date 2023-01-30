import datetime
import inspect
import os
import time
from typing import Union

from .configure_default import ConfigDefault
from .loger.loger import LogColor, log as _log
from .rewr.ini import get_ini_config, join_ini_config


def get_class_attributes(cls):
	attrs = []
	for i in inspect.getmembers(cls):
		if not i[0].startswith('_'):
			if not inspect.ismethod(i[1]):
				attrs.append(i)
	return attrs


def join_py_config(conf_py: Union[list, tuple, object] = ConfigDefault()):
	if not isinstance(conf_py, (list, tuple)):
		conf_py = [conf_py]
	
	_conf_py = ConfigDefault()
	for obj in conf_py:
		if callable(obj):
			attributes = get_class_attributes(obj())
		else:
			attributes = get_class_attributes(obj)
		for (k, v) in attributes:
			setattr(_conf_py, k, v)
	return _conf_py


def init_config_app(ini_path=None, conf_py: Union[list, tuple, object] = ConfigDefault(), task_id=None, get_loger=False):
	_task_id = f'{task_id}_' if task_id else ''
	
	_conf_py = join_py_config(conf_py)
	if ini_path is None:
		prefs = _conf_py
		ini_path = '/.dev/data'
	else:
		try:
			conf_ini = get_ini_config(os.path.join(ini_path, 'config.ini'))
			prefs = join_ini_config(conf_ini, _conf_py)
		except Exception as ex:
			_log(f'Exception', ex, level='debug')
			prefs = _conf_py
	iloger = LogColor(
		name=prefs.APP_NAME or __name__, save=prefs.LOGER_SAVE or False,
		stack=prefs.LOGER_STACK or False,
		stack_full=prefs.LOGER_STACK_FULL or False,
		disable=prefs.LOGER_DISABLE or False,
		log_path=f'{prefs.LOGER_PATH or "/.dev/logs"}/{_task_id}{datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d")}',
		humanize=prefs.LOGER_HUMANIZE,
		pid=True,
		level=prefs.LOGER_LEVEL
	)
	
	iloger.set_level(prefs.LOGER_LEVEL)
	try:
		prefs.DATA_DIR
	except Exception as ex:
		_log('Exception', ex, level='debug')
		prefs.DATA_DIR = ini_path
	if get_loger:
		return prefs, iloger
	return prefs, iloger.log
