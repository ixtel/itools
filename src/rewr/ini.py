import configparser


def read_number(a, just_try=True):
	"""
	:param a:
	:param just_try:
	:return:
	"""
	try:
		# First, we try to convert to integer.
		# (Note, that all integer can be interpreted as float and hex number.)
		return int(a)
	except Exception:
		# The integer convertion has failed because `a` contains others than digits [0-9].
		# Next try float, because the normal form (eg: 1E3 = 1000) can be converted to hex also.
		# But if we need hex we will write 0x1E3 (= 483) starting with 0x
		try:
			return float(a)
		except Exception:
			try:
				return int(a, 16)
			except Exception:
				try:
					r = eval(a)
					if callable(r):
						return a
					return r
				except Exception:
					if just_try:
						return a
					else:
						raise


def read_ini_config(path, section, variable):
	"""
	:param path:
	:param section:
	:param variable:
	:return:
	"""
	config = configparser.ConfigParser()
	config.read(path)
	res = config.get(section, variable)
	return read_number(res)


def get_ini_config(path):
	"""
	:param path:
	:return:
	"""
	config = configparser.ConfigParser()
	config.read(path)
	return config


def read_config_to_dict(path):
	"""
	:param path:
	:return:
	"""
	conf = get_ini_config(path)
	res = {}
	for each_section in conf.sections():
		each_section = each_section.upper()
		res[each_section] = {}
		for (each_key, each_val) in conf.items(each_section):
			res[each_section][each_key.upper()] = read_number(each_val)
	return res


def read_config_to_dict_variable(path):
	"""
	каждая секция это переменная, а значения секции это ключи словаря
	:param path:
	:return:
	"""
	cfg = get_ini_config(path)
	r = {}
	for each_section in cfg.sections():
		r[each_section] = {}
		for (each_key, each_val) in cfg.items(each_section):
			r[each_section][each_key] = each_val
	return r


def save_dict_to_config(path, dic):
	"""
	:param path:
	:param dic:
	:return:
	"""
	conf = get_ini_config(path)
	for section, variables in dic.items():
		for key, value in variables.items():
			conf.set(section.upper(), key.upper(), value)
	with open(path, "w") as config_file:
		conf.write(config_file)
	return None


def join_ini_config(conf_ini, conf_py):
	"""
	:param conf_ini:
	:param conf_py:
	:return:
	"""
	for each_section in conf_ini.sections():
		for (each_key, each_val) in conf_ini.items(each_section):
			if each_val.lower() == 'true':
				each_val = True
			elif each_val.lower() == 'false':
				each_val = False
			setattr(conf_py, each_key.upper(), read_number(each_val))
	return conf_py


class GetConfig:
	def __init__(self, path, section):
		"""
		:param path:
		:param section:
		"""
		self.path = path
		self.section = section
	
	def __getattr__(self, item):
		"""
		:param item:
		:return:
		"""
		try:
			return read_ini_config(self.path, self.section, item)
		except Exception as ex:
			print('Exception', ex)
			return None
