import hashlib


class Md5:
	def __init__(self):
		pass

	def md5(self, string):
		m = hashlib.md5()
		m.update(string.encode())
		return m.hexdigest()

	def md5Salt(self, string):
		for i in range(5):
			string = self.md5(string + "azxsw")
		return string
