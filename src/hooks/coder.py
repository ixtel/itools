def int_to_hex(x: int, n: int = 32) -> str:
	"""
	:param x:
	:param n:
	:return:
	"""
	return x.to_bytes(n, byteorder='big').hex()


def int_to_bytes(x: int) -> bytes:
	"""
	:param x:
	:return:
	"""
	return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def int_from_bytes(b: bytes) -> int:
	"""
	:param b:
	:return:
	"""
	return int.from_bytes(b, 'big')


def int_to_bytes_32(x: int) -> bytes:
	""""""
	return x.to_bytes(32, byteorder="big")
