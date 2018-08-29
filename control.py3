import mpd
import sys
import time
import os
PID = os.getpid()
MAX_ERROR = 50

def control(host='192.168.43.1', port='6600'):
	c = mpd.MPDClient()
	m = 0
	while 1:
		try:
			c.connect(host=host, port=str(port))
		except:
			print("Error firt connection !")
		
		q = input('ACTION: ')
		if q == 'exit' or q == 'quit':
			break
		func = str(q).split(" ", 1)[0]
		args = str(q).split(" ", 1)[1:]
		args = str(args).strip().split(" ")
		args = tuple(args)
		# print("args =", args)
		try:
			if q:
				x = c.hasattr(c, str(q).strip())(args)
				if x:
					print(x)
		except:
			m +=1
			if m == MAX_ERROR:
				break
			sys.stdout.write('re-connecting .')
			n = 1
			while 1:
				try:
					c.connect(host=host, port=str(port))
					break
				except:
					sys.stdout.write(".")
					n +=1
					time.sleep(1)
					if n == MAX_ERROR:
						print("MAX ATTEMP !")
						break

if __name__ == '__main__':
	print("PID:", PID)
	if len(sys.argv) == 1:
		control()
	else:
		c.control(*sys.argv)