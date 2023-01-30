import base64
import json

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import hashlib
# noinspection PyPackageRequirements
from Crypto.Cipher import AES
# noinspection PyPackageRequirements
from Crypto import Random
# noinspection PyPackageRequirements
from Crypto.Util.Padding import pad, unpad


def pass_to_key(password, salt):
	"""
	:param password:
	:param salt:
	:return:
	"""
	password_provided = password  # This is input in the form of a string
	password = password_provided.encode()  # Convert to type bytes
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=32,
		salt=salt,
		iterations=100000,
		backend=default_backend()
	)
	key = base64.urlsafe_b64encode(kdf.derive(password))  # Can only use kdf once
	return key


def dic_to_bytes(d):
	"""
	:param d:
	:return:
	"""
	b = json.dumps(d)
	b = str(b).encode()
	return b


def bytes_to_crypt(b, key):
	"""
	:param b:
	:param key:
	:return:
	"""
	cipher_suite = Fernet(key)
	c = cipher_suite.encrypt(b)
	return c


def crypt_resp(c, attr='result'):
	"""
	:param c:
	:param attr: 'result'
	:return:
	"""
	j = {attr: c.decode()}
	return j


def resp_crypt(d, attr='result'):
	"""
	:param d:
	:param attr: 'result'
	:return:
	"""
	c = d[attr].encode()
	return c


def crypt_dump(c, attr='result'):
	"""
	:param c:
	:param attr: 'result'
	:return:
	"""
	j = json.dumps({attr: c.decode()})
	return j


def crypt_load(d, attr='result'):
	"""
	:param d:
	:param attr: 'result'
	:return:
	"""
	c = json.loads(d)[attr].encode()
	return c


def crypt_to_bytes(c, key):
	"""
	:param c:
	:param key:
	:return:
	"""
	cipher_suite = Fernet(key)
	b = cipher_suite.decrypt(c)
	return b


def bytes_to_dic(b):
	"""
	:param b:
	:return:
	"""
	d = json.loads(b)
	return d


def dic_resp(d, key):
	"""
	:param d:
	:param key:
	:return:
	"""
	return crypt_resp(bytes_to_crypt(dic_to_bytes(d), key))


def resp_dic(d, key):
	"""
	:param d:
	:param key:
	:return:
	"""
	return bytes_to_dic(crypt_to_bytes(resp_crypt(d), key))


def dic_dump(d, key):
	"""
	:param d:
	:param key:
	:return:
	"""
	return crypt_dump(bytes_to_crypt(dic_to_bytes(d), key))


def dic_load(d, key):
	"""
	:param d:
	:param key:
	:return:
	"""
	return bytes_to_dic(crypt_to_bytes(crypt_load(d), key))


# TODO рефакторить весь модуль

class AesCipherECB:
	def __init__(self, password: str):
		"""
		:param password:
		
		<script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
		function sha256_sync(message) {
			// encode as UTF-8
			const msgBuffer = new TextEncoder().encode(message);
	
			// hash the message
			return crypto.subtle.digest('SHA-256', msgBuffer).then((hashBuffer) => {
				// convert ArrayBuffer to Array
				const hashArray = Array.from(new Uint8Array(hashBuffer));
				return hashArray.map(b => b.toString(16).padStart(2, '0')).slice(0, 8).join('')
			});
	
	
		}
	
		function decrypt(encrypted, password) {
			return sha256_sync(password).then((key) => {
				let key_encoded = CryptoJS.enc.Utf8.parse(key);
				let decrypted = CryptoJS.AES.decrypt(encrypted, key_encoded, {mode: CryptoJS.mode.ECB});
				let result = decrypted.toString(CryptoJS.enc.Utf8)
				return result
			})
		}
	
		decrypt('v66L6SlDrMK66aRd9jmwiQ==', '123').then((result) => {
			console.log(result)
		})
		
		№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№
		или синхронный вариант
		function decrypt(encrypted, password) {
			// let key = await sha256_sync(password)
			let key = new Hashes.SHA256().hex(password).slice(0, 16)
			let key_encoded = CryptoJS.enc.Utf8.parse(key);
			let decrypted = CryptoJS.AES.decrypt(encrypted, key_encoded, {mode: CryptoJS.mode.ECB});
			return decrypted.toString(CryptoJS.enc.Utf8)
		}
	
		let result = decrypt('v66L6SlDrMK66aRd9jmwiQ==', '123')
		console.log(result)
		"""
		self.key = hashlib.sha256(password.encode()).hexdigest()[:16]
		pass
	
	def encrypt(self, raw):
		"""
		:param raw:
		:return:
		"""
		raw = pad(raw.encode(), 16)
		cipher = AES.new(self.key.encode('utf-8'), AES.MODE_ECB)
		return base64.b64encode(cipher.encrypt(raw)).decode("utf-8", "ignore")
	
	def decrypt(self, enc):
		"""
		:param enc:
		:return:
		"""
		enc = base64.b64decode(enc)
		cipher = AES.new(self.key.encode('utf-8'), AES.MODE_ECB)
		return unpad(cipher.decrypt(enc), 16).decode("utf-8", "ignore")


class AesCipherCFB:
	def __init__(self, password: str):
		"""
		:param password:
		<script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>

		function decrypt_sync(encrypted, password) {
			let ciphertext = CryptoJS.enc.Base64.parse(encrypted)
			console.log('ciphertext', ciphertext)
			// split iv and ciphertext
			let iv = ciphertext.clone()
			iv.sigBytes = 16
			iv.clamp()
			ciphertext.words.splice(0, 4); // delete 4 words = 16 bytes
			ciphertext.sigBytes -= 16
			let _key = new Hashes.SHA256().hex(password).slice(0, 16)
			let key = CryptoJS.enc.Utf8.parse(_key)
	
			// decryption
			let decrypted = CryptoJS.AES.decrypt({ciphertext: ciphertext}, key, {
				iv: iv,
				mode: CryptoJS.mode.CFB
			});
			let result = decrypted.toString(CryptoJS.enc.Utf8)
			console.log(result)
			return result
		}
	
		let result_sync = decrypt_sync('9I9LHLTmfUAANwOZOsCwE9lGl1gY2fOd7keESO+Cr54=', 'test', 'ZYTPdQ==')
		console.log(result_sync) => test
		"""
		self.key = hashlib.sha256(password.encode()).hexdigest()[:16]
		self.BLOCK_SIZE = 16
		pass
	
	@staticmethod
	def pad(data):
		"""
		:param data:
		:return:
		"""
		length = 16 - (len(data) % 16)
		_pad = chr(length) * length
		return data + _pad
	
	@staticmethod
	def unpad(data):
		"""
		:param data:
		:return:
		"""
		return data[:-ord(data[-1])]
	
	def encrypt(self, message):
		"""
		:param message:
		:return:
		"""
		iv = Random.new().read(self.BLOCK_SIZE)
		aes = AES.new(self.key.encode('utf-8'), AES.MODE_CFB, iv, segment_size=128)
		_pad = self.pad(message)
		enc = aes.encrypt(_pad.encode('utf-8'))
		return base64.b64encode(iv + enc).decode('utf-8')
	
	def decrypt(self, encrypted):
		"""
		:param encrypted:
		:return:
		"""
		encrypted = base64.b64decode(encrypted)
		iv = encrypted[:self.BLOCK_SIZE]
		aes = AES.new(self.key.encode('utf-8'), AES.MODE_CFB, iv, segment_size=128)
		return self.unpad(aes.decrypt(encrypted[self.BLOCK_SIZE:]).decode('utf-8'))
