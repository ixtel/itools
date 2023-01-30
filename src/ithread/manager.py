from multiprocessing import Pool as pPool
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as tPool
from multiprocessing.managers import SyncManager
import subprocess

from ..config import log


def run_shell(cmd):
	"""
	:param cmd:
	:return:
	"""
	try:
		result = subprocess.check_output(cmd, shell=True).decode('utf-8')
		
		return result
	except Exception as ex:
		log('Exception', ex)
		return None


def worker(shared_manager_data_instance, function_to_run, process_n, thread_n):
	"""
	:param shared_manager_data_instance:
	:param function_to_run:
	:param process_n:
	:param thread_n:
	:return:
	"""
	log('START worker N =', process_n, 'thread N=', thread_n, level='info')
	while True:
		item = shared_manager_data_instance.get()
		if item is None:
			break
		else:
			function_to_run(item)
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
		log('START Process ', process_n, level='info')
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
			log('thread_pool _res', _res, level='info')
	except (KeyboardInterrupt, SystemExit):
		exit(0)
	return 'DONE Process {}'.format(process_n)


class SharedManagerData:
	def __init__(self, lock, data_items):
		"""
		:param lock:
		:param data_items:
		"""
		self.lock = lock
		self.data_items = data_items
	
	def get(self):
		"""
		:return:
		"""
		self.lock.acquire()
		try:
			item = self.data_items.pop(0)
		except Exception as _ex:
			item = None
		self.lock.release()
		return item


class SharedManager(SyncManager):
	pass


def process_pool(function_to_run, shared_data_items=None, process_per_cpu=1, threads_per_proces=10):
	"""
	:param function_to_run:
	:param shared_data_items:
	:param process_per_cpu:
	:param threads_per_proces:
	:return:
	"""
	if shared_data_items is None:
		shared_data_items = []
	log('Start processPool')
	max_process = int(cpu_count() * float(process_per_cpu))
	log('max_process', max_process)
	log('threads_per_proces', threads_per_proces)
	log('max_threads', max_process * threads_per_proces)
	
	SharedManager.register('SharedManagerDataSync', SharedManagerData)
	manager = SharedManager()
	manager.start()
	lock = manager.RLock()
	shared_manager_data_instance = getattr(manager, 'SharedManagerDataSync')(lock, shared_data_items)
	
	_res = []
	with pPool(max_process) as executor:
		multiple_results = [
			executor.apply_async(
				thread_pool,
				args=(
					shared_manager_data_instance,
					function_to_run,
					threads_per_proces,
					process_num,
				),
				callback=log
			) for process_num in range(max_process)
		]
		_res = [res.get() for res in multiple_results]
		log('processPool _res', _res)
	return _res


if __name__ == '__main__':
	try:
		process_pool(log, ['test'])
	except Exception as __ex:
		log(__ex)
