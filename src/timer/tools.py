import datetime
import time
from random import uniform, shuffle
from time import sleep
from typing import Union

import pytz


def now(time_int: Union[int, float] = None):
	"""
	:param time_int:
	:return:
	"""
	return int(time_int or time.time())


def formated_date_time(time_int: Union[int, float] = None, time_format: str = '%d-%m-%Y %H:%M:%S'):
	"""
	:param time_int:
	:param time_format: '%d-%m-%Y %H:%M:%S'
	:return: datetime format
	"""
	return datetime.datetime.fromtimestamp(now(time_int)).strftime(time_format)


def today(time_int: Union[int, float] = None):
	"""
	:param time_int:
	:return: day format
	"""
	# TODO today->index_day
	dt = datetime.datetime.fromtimestamp(now(time_int)).strftime
	day = '{}{}{}'.format(
		int(dt('%Y')),
		int(dt('%m')),
		int(dt('%d')))
	return day


def index_day(time_int: Union[int, float] = None):
	"""
	:param time_int:
	:return:
	"""
	return today(time_int)


def index_time(time_int: Union[int, float] = None):
	"""
	:param time_int:
	:return:
	"""
	dt = datetime.datetime.fromtimestamp(now(time_int)).strftime
	day = '{}{}{}{}{}'.format(
		str(dt('%Y')),
		str(dt('%m')),
		str(dt('%d')),
		str(dt('%H')),
		str(dt('%M')),
	)
	return day


def timestamp_from_dic(time_dict: dict = None):
	"""
	:param time_dict:
	:return:
	"""
	time_str = dict_format_date_time(time_dict)
	time_result = int(time.mktime(datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").timetuple()))
	return time_result


def timestamp_format_date_time(time_int: Union[int, float] = None):
	"""
	:param time_int:
	:return:
	"""
	time_dict = timestamp_to_dic(time_int)
	time_formated = dict_format_date_time(time_dict)
	return time_formated


def timestamp_format_date(time_int: Union[int, float] = None):
	"""
	:param time_int:
	:return:
	"""
	time_dict = timestamp_to_dic(time_int)
	date_formated = dict_format_date(time_dict)
	return date_formated


def dict_format_date_time(time_dict: dict = None):
	"""
	:param time_dict:
	:return:
	"""
	time_str = '%04d-%02d-%02d %02d:%02d:%02d' % (
		time_dict['year'], time_dict['month'], time_dict['day'], time_dict['hour'], time_dict['min'], time_dict['sec'])
	return time_str


def dict_format_date(time_dict: dict = None):
	"""
	:param time_dict:
	:return:
	"""
	time_str = '%04d %02d %02d' % (time_dict['year'], time_dict['month'], time_dict['day'])
	return time_str


def timestamp_to_dic(time_int: Union[int, float] = None):
	"""
	:param time_int:
	:return:
	"""
	dt = datetime.datetime.fromtimestamp(now(time_int)).strftime
	time_dict = {
		'year': int(dt('%Y')),
		'month': int(dt('%m')),
		'day': int(dt('%d')),
		'hour': int(dt('%H')),
		'min': int(dt('%M')),
		'sec': int(dt('%S')),
	}
	return time_dict


def iso_to_timestamp(time_str: str, time_format: str = "%Y-%m-%dT%H:%M:%S.%fZ"):
	"""
	:param time_str:
	:param time_format: "%Y-%m-%dT%H:%M:%S.%fZ"
	:return:
	"""
	r = int(datetime.datetime.strptime(time_str, time_format).timestamp())
	return r


def timestamp_in_tz(new_tz="Europe/Moscow"):
	"""
	:param new_tz:
	:return:
	"""
	new_timezone = pytz.timezone(new_tz)
	new_time_dict = datetime.datetime.now(new_timezone)
	new_timestamp = int(time.mktime(new_time_dict.timetuple()))
	return new_timestamp


def day_from_timestamp(time_int: Union[int, float] = None):
	"""
	:param time_int:
	:return:
	"""
	day = datetime.datetime.fromtimestamp(now(time_int))
	return day.replace(hour=0, minute=0, second=0, microsecond=0)


def count_between_days(time_from: Union[int, float], time_to: Union[int, float]):
	"""
	:param time_from:
	:param time_to:
	:return:
	"""
	return (day_from_timestamp(time_from) - day_from_timestamp(time_to)).days


def get_time_ago(time_int: Union[int, float]):
	return int((timestamp_in_tz() - int(time_int)) / 60)


def timestamps_between_days(time_from: Union[int, float], time_to: Union[int, float]):
	"""
	:param time_from:
	:param time_to:
	:return:
	"""
	day_from = day_from_timestamp(time_from)
	day_to = day_from_timestamp(time_to)
	x_days = (day_from - day_to).days
	result = []
	for i in range(x_days + 1):
		day_timestamp = int(day_from.timestamp() + i * 24 * 60 * 60)
		result.append(day_timestamp)
	return result


def slp(t1, t2=0):
	"""
	:param t1:
	:param t2:
	:return:
	"""
	if isinstance(t1, (list, tuple)):
		shuffle(t1)
		try:
			t2 = t1[0]
		except Exception as _ex:
			t2 = 0
		try:
			t1 = t1[1]
		except Exception as _ex:
			t1 = 0
	sleep(uniform(min(t1, t2), max(t1, t2)))
