import itertools
import random
import time
from multiprocessing import Pool as pPool
from multiprocessing.dummy import Pool as tPool
from multiprocessing.managers import SyncManager
from typing import Union

from ..hooks.power import file_flag_set, file_flag_get
from ..config import log


def worker(shared_manager_data_instance, function_to_run, process_n, thread_n):
	"""
	:param shared_manager_data_instance:
	:param function_to_run:
	:param process_n:
	:param thread_n:
	:return:
	"""
	log('START worker N =', process_n, 'thread N=', thread_n, level='DEBUG')
	try:
		function_to_run(shared_manager_data_instance)
	except Exception as ex:
		log('Exception', ex, 'function_to_run', function_to_run, level='WARNING')
	return 'DONE worker {} thread {}'.format(process_n, thread_n)


def worker_done(result):
	"""
	:param result:
	:return:
	"""
	log('DONE worker. result=', result)


def thread_pool(shared_manager_data_instance, function_to_run, max_threads, process_n):
	"""
	:param shared_manager_data_instance:
	:param function_to_run:
	:param max_threads:
	:param process_n:
	:return:
	"""
	try:
		log('START Process ', process_n, level='DEBUG')
		with tPool(max_threads) as executor:
			multiple_results = [
				executor.apply_async(
					worker,
					args=(
						shared_manager_data_instance,
						function_to_run,
						process_n,
						i
					),
					callback=worker_done
				) for i in range(max_threads)
			]
			_res = [res.get() for res in multiple_results]
			log('thread_pool _res', _res, level='DEBUG')
	except (KeyboardInterrupt, SystemExit):
		exit(0)
	return 'DONE Process {}'.format(process_n)


def __test_queue_reader(q):
	"""
	:param q:
	:return:
	"""
	i = 0
	while True:
		try:
			item = q.get()
		except Exception as ex:
			log('Exception', ex)
			item = None
		if item is None:
			i += 1
			log(f'sleep = {i}')
			time.sleep(i)
		else:
			i = 0
			log(f'item = {item}')
			yield item


def __test_queue_writer(q, value=random.random()):
	"""
	:param q:
	:param value:
	:return:
	"""
	i = 0
	while True:
		q.put(value)
		log('put Q')
		i += 3
		time.sleep(i)


class ListPassed:
	def __init__(self, *_args, **_kwargs):
		"""
		:param _args:
		:param _kwargs:
		"""
		self.source_worker = set()
		self.source_done = False
		pass
	
	@staticmethod
	def size():
		"""
		:return:
		"""
		return 0
	
	@staticmethod
	def isfull():
		"""
		:return:
		"""
		return False
	
	@staticmethod
	def get(info=False, label=''):
		"""
		:param info:
		:param label:
		:return:
		"""
		log(f'info={info} label={label}', level='debug')
		return {}
	
	def put(self, item):
		"""
		:param item:
		:return:
		"""
		pass
	
	def worker_join(self, worker_id):
		"""
		:param worker_id:
		:return:
		"""
		self.source_worker.add(worker_id)
	
	def worker_quit(self, worker_id):
		"""
		:param worker_id:
		:return:
		"""
		self.source_worker.remove(worker_id)
	
	def worker_is_done(self):
		"""
		:return:
		"""
		return len(self.source_worker) == 0
	
	def done(self):
		"""
		:return:
		"""
		self.source_done = True
	
	def is_done(self):
		"""
		:return:
		"""
		return self.source_done
	
	def show_info(self):
		"""
		:return:
		"""
		pass


class ListBase:
	def __init__(self, items=None, max_size=1024 ** 1):
		"""
		:param items:
		:param max_size:
		"""
		self.items = [] if items is None else items
		self.max_size = max_size
		self.source_done = False
		self.source_worker = set()
	
	def size(self):
		"""
		:return:
		"""
		return len(self.items)
	
	def isfull(self):
		"""
		:return:
		"""
		return self.size() >= self.max_size
	
	def get(self):
		"""
		:return:
		"""
		try:
			item = self.items.pop()
		except Exception as _ex:
			item = None
		return item
	
	def put(self, item):
		"""
		:param item:
		:return:
		"""
		try:
			self.items.append(item)
		except Exception as ex:
			log(f'Exception == {ex}', level='WARNING')
	
	def worker_join(self, worker_id):
		"""
		:param worker_id:
		:return:
		"""
		self.source_worker.add(worker_id)
	
	def worker_quit(self, worker_id):
		"""
		:param worker_id:
		:return:
		"""
		self.source_worker.remove(worker_id)
	
	def worker_is_done(self):
		"""
		:return:
		"""
		return len(self.source_worker) == 0
	
	def done(self):
		"""
		:return:
		"""
		self.source_done = True
	
	def is_done(self):
		"""
		:return:
		"""
		_done = self.source_done
		return _done
	
	def show_info(self):
		"""
		:return:
		"""
		log('List items:', self.items, level='INFO')


class ListMP(ListBase):
	def __init__(self, lock, items, max_size=1024 ** 1):
		"""
		:param lock:
		:param items:
		:param max_size:
		"""
		super().__init__(items=items, max_size=max_size)
		self.lock = lock
		self.items = items
		self.max_size = max_size
		self.source_done = False
		self.source_worker = set()
	
	def get(self):
		"""
		:return:
		"""
		self.lock.acquire()
		try:
			item = self.items.pop(0)
		except Exception as _ex:
			item = None
		self.lock.release()
		return item
	
	def put(self, item):
		"""
		:param item:
		:return:
		"""
		try:
			self.items.append(item)
		except Exception as ex:
			log(f'Exception == {ex}', level='WARNING')
		pass
	
	def worker_join(self, worker_id):
		"""
		:param worker_id:
		:return:
		"""
		self.lock.acquire()
		self.source_worker.add(worker_id)
		self.lock.release()
	
	def worker_quit(self, worker_id):
		"""
		:param worker_id:
		:return:
		"""
		self.lock.acquire()
		self.source_worker.remove(worker_id)
		self.lock.release()
	
	def worker_is_done(self):
		"""
		:return:
		"""
		return len(self.source_worker) == 0
	
	def done(self):
		"""
		:return:
		"""
		self.lock.acquire()
		self.source_done = True
		self.lock.release()
	
	def is_done(self):
		"""
		:return:
		"""
		_done = self.source_done
		return _done


class GenMP(ListMP):
	def __init__(self, lock, items, max_size=1024 ** 1):
		"""
		:param lock:
		:param items:
		:param max_size:
		"""
		super().__init__(lock=lock, items=items, max_size=max_size)
		self.lock = lock
		self.items = items
		self.max_size = max_size
		self.source_done = False
		self.source_worker = set()
	
	def get(self):
		"""
		:return:
		"""
		self.lock.acquire()
		try:
			item = next(self.items)
		except Exception as _ex:
			item = None
		self.lock.release()
		return item
	
	def put(self, item):
		"""
		:param item:
		:return:
		"""
		try:
			self.items = itertools.chain(self.items, item)
		except Exception as ex:
			log(f'Exception == {ex}', level='WARNING')
		pass


class TimerController:
	def __init__(self, delay=None):
		"""
		:param delay:
		"""
		self.delay = delay
		self.prev_time = time.time()
		if self.delay is None:
			self.release = self._release_none
		else:
			self.release = self._release
	
	@staticmethod
	def _release_none():
		"""
		:return:
		"""
		return True
	
	def _release(self):
		"""
		:return:
		"""
		_this_time = time.time()
		if _this_time - self.prev_time >= self.delay:
			self.prev_time = _this_time
			return True
		return False


class FlagMP(object):
	def __init__(self, lock):
		"""
		:param lock:
		"""
		self.lock = lock
		self.workers = 0
	
	def join(self):
		"""
		:return:
		"""
		self.lock.acquire()
		try:
			self.workers += 1
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
		self.lock.release()
	
	def quit(self):
		"""
		:return:
		"""
		self.lock.acquire()
		try:
			self.workers -= 1
			pass
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			pass
		self.lock.release()
	
	def is_done(self):
		"""
		:return:
		"""
		self.lock.acquire()
		is_done = self.workers == 0
		self.lock.release()
		return is_done
	
	def is_work(self):
		"""
		:return:
		"""
		self.lock.acquire()
		is_work = self.workers > 0
		self.lock.release()
		return is_work


class FlagFileMP(FlagMP):
	def __init__(self, lock, path, value_work=1, value_done=0):
		"""
		:param lock:
		:param path:
		:param value_work:
		:param value_done:
		"""
		super().__init__(lock)
		self.path = path
		self.value_work = value_work
		self.value_done = value_done
		file_flag_set(path, value_work)
	
	def is_done(self):
		"""
		:return:
		"""
		self.lock.acquire()
		is_done = file_flag_get(self.path) == self.value_done
		self.lock.release()
		return is_done
	
	def is_work(self):
		""""""
		self.lock.acquire()
		is_work = file_flag_get(self.path) == self.value_work
		self.lock.release()
		return is_work


class SharedManager(SyncManager):
	def get(self):
		"""
		:return:
		"""
		return


# TODO SHARED_OBJECT_MAP = {
# 	dict: DictMP
# }


def build_shared_manager(shared_object=Union[ListMP, ListBase, FlagMP], params=None):
	"""
	:param shared_object: Union[ListMP, ListBase, FlagMP]
	:param params:
	:return:
	"""
	if params is None:
		params = dict()
	SharedManager.register('MpSyncManager', shared_object)
	manager = SharedManager()
	manager.start()
	lock = manager.RLock()
	shared_manager_data_instance = getattr(manager, 'MpSyncManager')(lock=lock, **params)
	return shared_manager_data_instance


class PoolMpAsync:
	def __init__(self, pool=None):
		"""
		:param pool:
		"""
		self.pool = [] if pool is None else pool
	
	def add(self, count=1, handler=log, params=None, callback=None, error_callback=log):
		"""
		:param count:
		:param handler:
		:param params:
		:param callback:
		:param error_callback:
		:return:
		"""
		if params is None:
			params = {}
		for i in range(count):
			item = (
				handler,
				params,
				callback,
				error_callback,
			)
			self.pool.append(item)
		return self
	
	def run(self):
		"""
		:return:
		"""
		max_process = len(self.pool)
		log(f'process count == {max_process}', level='info')
		if max_process == 1:
			result = []
			for process_num, (func, params, callback, error_callback) in enumerate(self.pool):
				value = func(process_num, params=params)
				result.append(value)
			return result
		else:
			for func, params, callback, error_callback in self.pool:
				log(f'func={func}, params={params}, callback={callback}, error_callback={error_callback}', level='debug')
			
			results = []
			with pPool(max_process) as pool:
				try:
					jobs = []
					for process_num, (func, params, callback, error_callback) in enumerate(self.pool):
						_worker = pool.apply_async(
							func=func,
							args=(process_num,),
							kwds={'params': params},
							callback=callback,
							error_callback=error_callback,
						)
						jobs.append(_worker)
					log('jobs', len(jobs), jobs)
					for result in jobs:
						time.sleep(2)
						try:
							value = result.get()
						except KeyboardInterrupt:
							log("Interrupted by user")
							pool.terminate()
							break
						except Exception as ex:
							log(f'Exception {ex}', level='critical')
							value = ex
						log('PoolMpAsync value', value)
						results.append(value)
				except Exception as ex:
					log(f'Exception {ex}', level='critical')
					raise ex
				finally:
					pool.close()
					pool.join()
			log('processPool results', results, level='info')
			return results


class PoolWithFlag(PoolMpAsync):
	"""
	Создание и запуск пула с воркерами
	"""
	
	def __init__(self, *args, **kwargs):
		"""
		# флаг для db server (zmq or socks)
		:param args:
		:param kwargs:
		"""
		super().__init__(*args, **kwargs)
		self.flag = build_shared_manager(
			shared_object=FlagMP,
		)
	
	def add(self, count=1, handler=log, params=None, callback=None, error_callback=log):
		"""
		# добавляем воркера в пул
		:param count:
		:param handler:
		:param params:
		:param callback:
		:param error_callback:
		:return:
		"""
		params = dict() if params is None else params.copy()
		params.update(dict(flag=self.flag))
		super().add(
			count=count,
			handler=handler,
			params=params,
			callback=callback, error_callback=error_callback,
		)
	
	def run(self):
		"""
		# запускаем пул
		:return:
		"""
		log('pool_map', self.pool, level='DEBUG')
		super().run()
