import os
import sys
import mpd
import traceback
HOST = '192.168.43.1'
if os.getenv('MPD_HOST'):
	HOST = os.getenv('MPD_HOST')
PORT = 6600
CLIENT = ''
import time
import cmdw3
from make_colors import make_colors

def makeList(alist, ncols, vertically=True, file=None):
    from distutils.version import StrictVersion # pep 386
    import prettytable as ptt # pip install prettytable
    import sys
    assert StrictVersion(ptt.__version__) >= StrictVersion('0.7') # for PrettyTable.vrules property        
    L = alist
    nrows = - ((-len(L)) // ncols)
    ncols = - ((-len(L)) // nrows)
    t = ptt.PrettyTable([str(x) for x in range(ncols)])
    t.header = False
    t.align = 'l'
    t.hrules = ptt.NONE
    t.vrules = ptt.NONE
    r = nrows if vertically else ncols
    chunks = [L[i:i+r] for i in range(0, len(L), r)]
    chunks[-1].extend('' for i in range(r - len(chunks[-1])))
    if vertically:
        chunks = zip(*chunks)
    for c in chunks:
        t.add_row(c)
    print(t)

def conn0(host="192.168.43.1", port=6600, playlist="radio", columns=200):
     global mpd_client
     global mpd_host
     global mpd_port
     global diplay_columns
     global stations
     mpd_host = host
     mpd_port = port
     diplay_columns = columns
     mpd_client = MPDClient()
     mpd_client.timeout = 20
     mpd_client.idletimeout = None
     mpd_client.connect(mpd_host, mpd_port)
     return mpd_client


def conn(host=None, port=6600):
	global HOST
	global PORT
	CLIENT = ''
	mpd_client = mpd.MPDClient()
	while 1:
		try:
			if host and port:
				HOST = host
				PORT = port
			# print("HOST =", HOST)
			# print("PORT =", PORT)
			mpd_client.connect(host=HOST, port=PORT)
			break
		except:
			time.sleep(0.03)
	mpd_client.timeout = 20
	mpd_client.idletimeout = None
	return mpd_client

def organizer_album_by_artist(results):
	albums = []
	#paths = []
	album_paths = {}
	n = 1
	for i in results:
		albums.append(i.get('album'))
		#paths.append(os.path.dirname(i.get(file)))
	album = set(albums)
	for i in album:
		for x in results:
			if x.get('album') == i:
				album_paths.update(
					{
						n: {
							'album':i,
							'path':os.path.dirname(x.get('file')),
						}
					}
				)
				break
		n+=1
	return album_paths

def navigator_find(x, host=None):
	for i in x:
		print(str(i) + ". " + "Album: " + make_colors(x.get(i).get('album'), 'white', 'blue'))
		print(" "*len(str(i)) + "  " + "Path : " + make_colors(x.get(i).get('path'), 'white', 'magenta'))
		print("-----------------------" + ("-" * len(x.get(i).get('path'))) + "--")
	q = input('Play Album [number]: ')
	if q:
		if str(q).isdigit():
			if not int(q) > len(x.keys()):
				command_execute('clear', host)
				command_execute('add %s'%(x.get(int(q)).get('path')))
				command_execute('play') 


def command_execute(commands, host=None):
	if isinstance(commands, list):
		commands = " ".join(commands)
	CLIENT = conn(host)
	# print("commands =", commands)
	if 'album' in commands or 'find' in commands:
		commands = str(commands).strip().split(' ', 2)
	elif 'add' in commands:
		commands = str(commands).strip().split(' ', 1)
	else:
		commands = str(commands).strip().split(' ')
	# print("commands tuple =", (tuple(commands[1:])))
	print("COMMAND :", " ".join(commands))
	if len(commands) > 1:
		args = tuple(commands[1:])
		# print("ARGS =", args)
		x = getattr(CLIENT, commands[0])(*args)
		if x:
			if 'find' in commands:
				x = organizer_album_by_artist(x)
				navigator_find(x, host)
			elif 'list' in commands:
				x2 = []
				for i in x:
					x2.append(str(x.index(i)) + ". " + i)
				makeList(x2, 10,)
			else:
				print(x)
		print("#"*cmdw3.getWidth())
	else:
		x = getattr(CLIENT, commands[0])()
		if x:
			print(x)
		print("#"*cmdw3.getWidth())

def execute(host=None, commands=None):
	# print("commands =", commands)
	if not commands:
		q = input('FUNCTION: ')
	else:
		q = commands
	if isinstance(q, list):
		q = " ".join(q)
	# print("COMMAND XXX =", q)
	if "#" in q:
		list_command = str(q).strip().split("#")
		# print("list_command =", list_command)
		for i in list_command:
			command_execute(str(i).strip(), host)
	else:
		command_execute(q, host)
		

if __name__ == '__main__':
	print("PID: ", os.getpid())
	# print("len(sys.argv) =", len(sys.argv))
	if len(sys.argv) == 2:
		if len(str(sys.argv[1]).strip().split(".")) == 4:
			execute(host=sys.argv[1])
		else:
			execute(commands=sys.argv[1:])
	elif len(sys.argv) > 2:
		if len(str(sys.argv[1]).strip().split(".")) == 4:
			print("sys.argv[2:] =", sys.argv[2:])
			execute(host=sys.argv[1], commands=sys.argv[2:])
		else:		
			# print("sys.argv[1:] =", sys.argv[1:])
			execute(commands=sys.argv[1:])		

	else:
		execute()



