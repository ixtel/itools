from src.loger.loger import log
from src.hooks.crypt import AesCipherCFB

if __name__ == '__main__':
	enc = AesCipherCFB('test').encrypt('test')
	log(enc)
	dec = AesCipherCFB('test').decrypt(enc)
	log(dec)
