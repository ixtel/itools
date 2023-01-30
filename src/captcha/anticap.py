import os
import time

from ..config import log
from ..timer.tools import slp
from python3_anticaptcha import ImageToTextTask, AntiCaptchaControl
from python_rucaptcha import ImageCaptcha, RuCaptchaControl

from ..network.tools import save_file_from_url

__all__ = ('ClientAntiGate', 'ClientRuCaptcha', 'AntiCaptchaClient', 'get_client',)


class ClientBase:
	def __init__(self, *_, **__):
		self.gate = None
		self.ctrl = None
	
	def get_key(self, file_obj):
		"""
		:param file_obj:
		:return:
		"""
		try:
			res = self.gate.captcha_handler(captcha_file=file_obj)
			return res
		except Exception as ex:
			log('Exception', ex)
			return None
	
	def _send_report(self, task_id):
		"""
		:param task_id:
		:return:
		"""
		return None, None
	
	def send_report(self, task_id):
		"""
		:param task_id:
		:return:
		"""
		res = False
		error_id = 1
		repeated = 10
		i = 0
		while error_id != 0 or i < repeated:
			i += 1
			try:
				res, error_id = self._send_report(task_id)
			except Exception as ex:
				log('Exception', ex)
				error_id = 1
		return res
	
	def _get_answer(self, key):
		"""
		:param key:
		:return:
		"""
		return None, None
	
	def get_answer(self, file_path):
		"""
		:param file_path:
		:return:
		"""
		key = self.get_key(file_path)
		answer, error_code = self._get_answer(key)
		log('answer', answer, 'error_code', error_code, file_path)
		
		try:
			task_id = key['taskId']
		except Exception as _ex:
			task_id = None
		return answer, task_id
	
	@staticmethod
	def get_image(captcha_url, file_path, proxy=None, cookies=None, user_agent=None):
		"""
		:param captcha_url:
		:param file_path:
		:param proxy:
		:param cookies:
		:param user_agent:
		:return:
		"""
		try:
			if captcha_url is not None:
				proxy_type = None
				auth = None
				proxy_str = None,
				if proxy and isinstance(proxy, dict):
					if proxy.get('login') and proxy.get('pas'):
						auth = [proxy['login'], proxy['pas']]
					else:
						auth = None
					proxy_str = f'{proxy["ip"]}:{proxy["port"]}'
					proxy_type = proxy.get('typ', 'http')
				save_file_from_url(
					url=captcha_url,
					proxy=proxy_str,
					timeout=60,
					auth=auth,
					proxy_type=proxy_type,
					file_name=file_path,
					cookies=cookies,
					user_agent=user_agent,
				)
			return captcha_url
		except Exception as ex:
			log('Exception', proxy, ex)
			raise ex
	
	def get(self, captcha_url, cur_dir, proxy=None, repeated=3, get_image_callback=None, cookies=None, user_agent=None):
		"""
		:param captcha_url:
		:param cur_dir:
		:param proxy:
		:param repeated:
		:param get_image_callback:
		:param cookies:
		:param user_agent:
		:return:
		"""
		text = None
		task_id = None
		
		file_name = str(time.time())
		if not os.path.exists(cur_dir):
			os.mkdir(cur_dir)
		_ext = 'jpg'
		
		file_path = os.path.join(cur_dir, '%s_captcha.%s' % (file_name, _ext))
		
		try:
			if get_image_callback is None:
				self.get_image(captcha_url=captcha_url, file_path=file_path, proxy=proxy, cookies=cookies, user_agent=user_agent)
			else:
				get_image_callback(captcha_url, file_path)
		except Exception as ex:
			log('Exception', ex)
			file_path = None
		
		if file_path is not None:
			for i in range(repeated):
				text, task_id = self.get_answer(file_path)
				if text is None:
					slp(10, 15)
					continue
				else:
					break
		return text, file_path, task_id


class ClientAntiGate(ClientBase):
	def __init__(self, apikey=None, sleep_time=10, language='ru', phrase=False, regsense=False, *_, **__):
		"""
		:param apikey:
		:param sleep_time:
		:param language:
		:param phrase:
		:param regsense:
		:param _:
		:param __:
		"""
		super().__init__(*_, **__)
		self.gate = ImageToTextTask.ImageToTextTask(anticaptcha_key=apikey, sleep_time=sleep_time, language=language, phrase=phrase, case=regsense)
		self.ctrl = AntiCaptchaControl.AntiCaptchaControl(anticaptcha_key=apikey)
	
	def _send_report(self, task_id):
		"""
		:param task_id:
		:return:
		"""
		res = self.ctrl.complaint_on_result(task_id)
		error_id = res.get('errorId', 1)
		return res, error_id
	
	def _get_answer(self, key):
		"""
		:param key:
		:return:
		"""
		answer = None
		error_code = None
		try:
			answer = key['solution']['text']
		except Exception as ex:
			log('Exception', ex, key)
			try:
				error_code = key['errorCode']
			except Exception as _ex:
				pass
		return answer, error_code


class ClientRuCaptcha(ClientBase):
	def __init__(self, apikey=None, sleep_time=10, language='ru', phrase=False, regsense=False, *_, **__):
		"""
		:param apikey:
		:param sleep_time:
		:param language:
		:param phrase:
		:param regsense:
		:param _:
		:param __:
		"""
		super().__init__(*_, **__)
		self.gate = ImageCaptcha.ImageCaptcha(
			rucaptcha_key=apikey, sleep_time=sleep_time, language=0, lang=language, phrase=int(phrase),
			regsense=int(regsense)
		)
		self.ctrl = RuCaptchaControl.RuCaptchaControl(rucaptcha_key=apikey)
	
	def _send_report(self, task_id):
		"""
		:param task_id:
		:return:
		"""
		res = self.ctrl.additional_methods(action="reportbad", id=task_id)
		error_id = res.get('error', 1)
		return res, error_id
	
	def _get_answer(self, key):
		"""
		:param key:
		:return:
		"""
		answer = None
		error_code = None
		try:
			answer = key['captchaSolve']
		except Exception as ex:
			log('Exception', ex, key)
			try:
				error_code = key['error']
			except Exception as _ex:
				pass
		return answer, error_code


CLIENT_MAP = dict(
	rucaptcha=ClientRuCaptcha,
	anticaptcha=ClientAntiGate,
	antigate=ClientAntiGate,
)


def get_client(name):
	"""
	:param name:
	:return:
	"""
	return CLIENT_MAP.get(name, ClientRuCaptcha)


AntiCaptchaClient = ClientRuCaptcha
