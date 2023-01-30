import datetime
import inspect
import logging
import os
import time

import colorama
import coloredlogs
from humanize import precisedelta
from colorama import Back, Fore, Style

from .helper import text_to_file

colorama.init()

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_nameToLevel = {
	'CRITICAL': CRITICAL,
	'FATAL': FATAL,
	'ERROR': ERROR,
	'WARN': WARNING,
	'WARNING': WARNING,
	'INFO': INFO,
	'DEBUG': DEBUG,
	'NOTSET': NOTSET,
	'critical': CRITICAL,
	'fatal': FATAL,
	'error': ERROR,
	'warn': WARNING,
	'warning': WARNING,
	'info': INFO,
	'debug': DEBUG,
	'notset': NOTSET,
	'50': CRITICAL,
	'40': ERROR,
	'30': WARNING,
	'20': INFO,
	'10': DEBUG,
	'0': NOTSET,
	50: CRITICAL,
	40: ERROR,
	30: WARNING,
	20: INFO,
	10: DEBUG,
	0: NOTSET,
}

_levelToName = {
	50: 'critical',
	40: 'error',
	30: 'warning',
	20: 'info',
	10: 'debug',
	0: 'notset',
}


def caller_name(parentframe):
	"""
	:param parentframe:
	:return:
	"""
	name = []
	module = inspect.getmodule(parentframe)
	if module:
		name.append(module.__name__)
	if 'self' in parentframe.f_locals:
		name.append(parentframe.f_locals['self'].__class__.__name__)
	codename = parentframe.f_code.co_name
	if codename != '<module>':  # top level usually
		name.append(codename)  # function or a method
	return ".".join(name)


formatter = coloredlogs.ColoredFormatter(
	fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	datefmt='%d.%m.%Y %H:%M',
)


# noinspection PyPep8Naming
class iLog:
	# noinspection PyUnresolvedReferences
	def __init__(
			self,
			level='DEBUG',
			name='MyProject',
			disable=False,
			save=False,
			log_path=None,
			stack=False,
			stack_full=True,
			stack_cls=False,
			pid=False,
			default_dir='dev_log',
			humanize=True
	):
		"""
		:param level:
		:param name:
		:param disable:
		:param save:
		:param log_path:
		:param stack:
		:param stack_full:
		:param stack_cls:
		:param pid:
		:param default_dir:
		:param humanize:
		"""
		logging_level = _nameToLevel[level]
		
		self.logging_level = logging_level
		self.name = f'iLog_{name}[{os.getpid()}]'
		if humanize:
			self.humanize_formater = precisedelta
		else:
			self.humanize_formater = lambda x: x
		
		try:
			logging.root.manager.loggerDict.pop(self.name)
		except Exception as _ex:
			pass
		
		logging.basicConfig(level=logging_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		
		logger = logging.getLogger(self.name)
		
		self.logger = logger
		
		handler = logging.StreamHandler()
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		logger.propagate = False
		
		self.disabled = disable
		logger.disabled = self.disabled
		
		self.timer = {
			'default': time.time()
		}
		self.save = save
		self.stack = stack
		self.pid = pid
		self.stack_full = stack_full
		self.stack_cls = stack_cls
		if log_path:
			self.log_path = log_path
		else:
			_root = os.path.abspath('/')
			log_dir = os.path.abspath(
				os.path.normpath(
					'{}/{}/{}'.format(
						_root,
						default_dir,
						name
					)
				)
			)
			self.log_path = f'{log_dir}/{self.pid}_{datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d")}.txt'
			os.makedirs(log_dir, exist_ok=True)
		
		self.set_level(logging_level)
	
	def __timer_set(self, name):
		"""
		:param name:
		:return:
		"""
		self.timer[name] = time.time()
	
	def __timer_get(self, name):
		"""
		:param name:
		:return:
		"""
		_ct = time.time()
		_st = self.timer.get(name, _ct)
		self.__timer_set(_st)
		tm = _ct - _st
		return tm
	
	# noinspection PyUnresolvedReferences
	def set_level(self, level=None):
		"""
		:param level:
		:return:
		"""
		if level is None:
			level = self.logging_level
		else:
			level = _nameToLevel[level]
		loggers = [logging.getLogger(_name) for _name in logging.root.manager.loggerDict if not _name.startswith('iLog')]
		for logger in loggers:
			# отключем DEBUG внешних модулей
			logger.setLevel(logging.INFO)
		
		self.logger.setLevel(int(level))
		return
	
	def log_gen(
			self,
			*args,
			end='\n',
			level='info',
	):
		"""
		:param args:
		:param end: '\n'
		:param level: 'info'
		:return:
		"""
		out = ''
		if self.disabled is False:
			if _nameToLevel[level] < self.logging_level:
				return out
			args = list(args)
			args = list(map(str, args))
			_stack = ''
			if self.stack:
				try:
					stack_arr = [f'{f[2]}.{caller_name(f[0])}' for f in inspect.stack()]
					stack_arr = list(
						filter(lambda x: x.split('.')[-1] not in ['wrapped', 'logtimer', 'timed', 'timedwrapped'], stack_arr[2:-1]))
					if self.stack_full is False:
						try:
							stack_arr = [stack_arr[0]]
						except Exception as _ex:
							pass
					stack = []
					for i, _s in enumerate(stack_arr):
						stack.append('    ' * i + _s)
					_stack = end.join(stack)
				except Exception as _ex:
					print('Stack ex', _ex)
					pass
			out = ' '.join(args) + '     ' + _stack
		return out
	
	def log(self, *args, end='\n', level='info', **__kwargs):
		"""
		:param args:
		:param end: '\n'
		:param level: 'info'
		:param __kwargs:
		:return:
		"""
		out = self.log_gen(*args, end=end, level=level)
		if self.save and out and out != end:
			text_to_file(f'{out}{end}', self.log_path, 'a')
		_loger = getattr(self.logger, _levelToName[_nameToLevel[level]])
		_loger(out)
		return out
	
	def logtimer(self, name, *args, **kwargs):
		"""
		:param name:
		:param args:
		:param kwargs:
		:return:
		"""
		tm = self.__timer_get(name)
		if tm:
			kwargs['level'] = '50'
			return self.log(
				name, 'TIMER ==', self.humanize_formater(tm), *args, **kwargs
			)
		else:
			self.__timer_set(name)
			return None
	
	def timeit(self, method):
		"""
		:param method:
		:return:
		"""
		def timed(*args, **kw):
			if self.disabled is False:
				self.timer[method.__name__] = time.time()
			self.__timer_set(method.__name__)
			result = method(*args, **kw)
			tm = self.__timer_get(method.__name__)
			self.log(method.__name__, self.humanize_formater(tm))
			return result
		
		return timed


class LogColor(iLog):
	def __init__(self, *args, **kwargs):
		"""
		:param args:
		:param kwargs:
		"""
		super().__init__(*args, **kwargs)
	
	def start(self, *args, **kwargs):
		"""
		:param args:
		:param kwargs:
		:return:
		"""
		self.log(Back.GREEN, Fore.LIGHTMAGENTA_EX, *args, Style.RESET_ALL, **kwargs)
	
	def stop(self, *args, **kwargs):
		"""
		:param args:
		:param kwargs:
		:return:
		"""
		self.log(Back.RED, Fore.BLUE, *args, Style.RESET_ALL, **kwargs)
	
	def debug(self, *args, **kwargs):
		"""
		:param args:
		:param kwargs:
		:return:
		"""
		self.log(Back.WHITE, Fore.BLACK, *args, Style.RESET_ALL, **kwargs)
	
	def info(self, *args, **kwargs):
		"""
		:param args:
		:param kwargs:
		:return:
		"""
		self.log(Back.CYAN, Fore.BLUE, *args, Style.RESET_ALL, **kwargs)
	
	def warning(self, *args, **kwargs):
		"""
		:param args:
		:param kwargs:
		:return:
		"""
		self.log(Back.YELLOW, Fore.LIGHTRED_EX, *args, Style.RESET_ALL, **kwargs)
	
	def error(self, *args, **kwargs):
		"""
		:param args:
		:param kwargs:
		:return:
		"""
		self.log(Style.BRIGHT + Back.RED, Fore.LIGHTYELLOW_EX, *args, Style.RESET_ALL, **kwargs)
	
	def critical(self, *args, **kwargs):
		"""
		:param args:
		:param kwargs:
		:return:
		"""
		self.log(Style.BRIGHT + Back.BLACK, Fore.LIGHTWHITE_EX, '-' * 40, Style.RESET_ALL, **kwargs)
		self.log(Style.BRIGHT + Back.BLACK, Fore.LIGHTWHITE_EX, *args, Style.RESET_ALL, **kwargs)
		self.log(Style.BRIGHT + Back.BLACK, Fore.LIGHTWHITE_EX, '-' * 40, Style.RESET_ALL, **kwargs)


loger = LogColor()
log = loger.log
timeit = loger.timeit
logtimer = loger.logtimer
