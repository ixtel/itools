from __future__ import print_function

import time

import colorama
from termcolor import colored

colorama.init()
st = False
inters = True


def main(name):
	"""
	:param name:
	:return:
	"""
	print("\n{} {} {}".format(
		colored("============", 'cyan', attrs=['bold']),
		colored(name, 'red', attrs=['bold']),
		colored("============", 'cyan', attrs=['bold']),
		end='\n\n'
	)
	)


def section(name):
	"""
	:param name:
	:return:
	"""
	print("\n{} {}".format(
		colored("#", 'cyan', attrs=['bold']),
		colored(name, attrs=['bold'])
	)
	)


def task(name):
	"""
	:param name:
	:return:
	"""
	print('{} {}'.format(
		colored("==>", 'green', attrs=['bold']),
		colored(name, 'green', attrs=['bold'])
	)
	)


def subtask(name):
	"""
	:param name:
	:return:
	"""
	print('{} {}'.format(
		colored("  ->", 'yellow', attrs=['bold']),
		colored(name, 'yellow', attrs=['bold'])
	)
	)


def result(name):
	"""
	:param name:
	:return:
	"""
	print('{} {}'.format(
		colored("<==", 'cyan', attrs=['bold']),
		colored(name, 'cyan', attrs=['bold']))
	)


def subresult(name):
	"""
	:param name:
	:return:
	"""
	print('{} {}'.format(
		colored("  <-", 'cyan', attrs=['bold']),
		colored(name, 'magenta', attrs=['bold']))
	)


def failure(name):
	"""
	:param name:
	:return:
	"""
	print('{} {}'.format(
		colored("==! ERROR:", 'red', attrs=['bold']),
		colored(name, attrs=['bold'])
	)
	)


def subfailure(name):
	"""
	:param name:
	:return:
	"""
	print('{} {}'.format(
		colored("  -!", 'red', attrs=['bold']),
		colored(name, 'red', attrs=['bold'])
	)
	)


def prompt(name):
	"""
	:param name:
	:return:
	"""
	print('{} {}'.format(
		colored("==", 'magenta', attrs=['bold']),
		colored(name, attrs=['bold'])),
		end="\n"
	)


def subprompt(name):
	"""
	:param name:
	:return:
	"""
	print('{} {}'.format(
		colored("  --", 'magenta', attrs=['bold']),
		colored(name, attrs=['bold'])),
		end="\n")


def debug(name):
	"""
	:param name:
	:return:
	"""
	print('{} {}'.format(
		colored("DEBUG", 'red', attrs=['bold']),
		colored(name, 'red', 'on_white')),
		end="\n"
	)


def timeline(name):
	"""
	:param name:
	:return:
	"""
	print('{} {}'.format(
		colored("Timer", 'cyan', attrs=['bold']),
		colored(name, 'red', 'on_white')),
		end="\n"
	)


def timer(name):
	"""
	:param name:
	:return:
	"""
	global st
	if st is False:
		st = time.time()
	ct = time.time()
	runing = ct - st
	if inters:
		runing = int(runing)
	st = ct
	timeline(str(name) + ': runing: ' + str(runing))
