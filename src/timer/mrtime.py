import datetime
from datetime import timezone


def get_date(date):
	"""
	:param date:
	:return:
	"""
	ts = datetime.datetime.utcfromtimestamp(int(date))
	return ts.strftime('%d.%m.%Y %H:%M:%S')


def pack_date(day, month, year, hour=0, minute=0, second=0, mili_second=0):
	"""
	:param day:
	:param month:
	:param year:
	:param hour:
	:param minute:
	:param second:
	:param mili_second:
	:return:
	"""
	h = datetime.datetime(day, month, year, hour, minute, second, mili_second)
	t = h.replace(tzinfo=timezone.utc).timestamp()
	return int(t)
