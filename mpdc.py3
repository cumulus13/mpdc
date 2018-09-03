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
from debug import debug
from make_colors import make_colors
import re

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
			debug(HOST=HOST)
			debug(PORT=PORT)
			mpd_client.connect(host=HOST, port=PORT)
			break
		except:
			time.sleep(0.03)
	mpd_client.timeout = 20
	mpd_client.idletimeout = None
	return mpd_client

def organizer_album_by_artist(results):
	# print ("results =", results[1])
	albums = []
	#paths = []
	album_paths = {}
	n = 1
	for i in results:
		# print ("i =",i)
		if isinstance(i, list):
			for x in i:
				albums.append(x.get('album'))
		else:		
			albums.append(i.get('album'))
		#paths.append(os.path.dirname(i.get(file)))
	album = set(albums)
	# print("album =", album)
	for i in album:
		for x in results:
			if isinstance(x, list):
				for y in x:
					if y.get('album') == i:
						album_paths.update(
							{
								n: {
									'album':i,
									'path':os.path.dirname(y.get('file')),
								}
							}
						)
						# n+=1
						break		
			else:
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

def navigator_find(x, host=None, clear=True):
	play_root=False
	multiplay=False
	def executor(q):
		# print ("play_root =", play_root)
		if str(q).isdigit():
			if not int(q) > len(x.keys()):
				if play_root:
					path = os.path.dirname(x.get(int(q)).get('path'))
					debug(path=path)
					# print ("path 0 =",path)
					command_execute('add %s'%(path))
				else:
					path = x.get(int(q)).get('path')
					debug(path=path)
					# print ("path 1 =",path)
					command_execute('add %s'%(path))
				if not multiplay:
					command_execute('play') 
	for i in x:
		print(str(i) + ". " + "Album: " + make_colors(x.get(i).get('album'), 'white', 'blue'))
		print(" "*len(str(i)) + "  " + "Path : " + make_colors(x.get(i).get('path'), 'white', 'magenta'))
		print("-----------------------" + ("-" * len(x.get(i).get('path'))) + "--")
	q = input('Play Album [number]: ')
	if q:
		if clear:
			command_execute('clear', host)
		if "," in q or " " in q or "|" in q or ";" in q:
			multiplay=True
			q1 = re.split(",| |;|\|", q)
			debug(q1=q1)
			# print("q1 =", q1)
			q2 = []
			for i in q1:
				if not str(i).strip() == '':
					q2.append(i)
				if str(i).strip() == '-1':
					play_root=True
			for i in q2:
				executor(i)
			if multiplay:
				command_execute('play')
		else:
			executor(q)

def command_execute(commands, host=None):
	n_list = 10
	x_find = False
	# debug('commands_execute')
	if isinstance(commands, list):
		commands = " ".join(commands)
	CLIENT = conn(host)
	# debug('commands_execute', "CLIENT")
	debug(commands=commands)
	if 'album' in commands or 'find' in commands:
		commands = str(commands).strip().split(' ', 2)
	elif 'add' in commands:
		commands = str(commands).strip().split(' ', 1)
	else:
		commands = str(commands).strip().split(' ')
	# print("commands tuple =", (tuple(commands[1:])))
	for i in commands:
		if i[0] == 'N' and i[1].isdigit():
			n_list = int(i[1:])
			commands.remove(i)
	print("COMMAND :", " ".join(commands))
	if len(commands) > 1:
		args = tuple(commands[1:])
		# print("ARGS =", args)
		if 'album' in commands and 'find' in commands:
			x = getattr(CLIENT, commands[0])(*args)
			if not x:
				debug("not x")
				x = getattr(CLIENT, 'list')('album')
				debug(len_x = len(x))
				debug(commands_index_album_add = commands[commands.index('album') + 1].lower())
				x_find_album = []
				for i in x:
					if commands[commands.index('album') + 1].lower() in str(i).lower():
						x1 = getattr(CLIENT, 'find')('album', i)
						x_find_album.append(x1)
				x = x_find_album
				x_find = True
		else:
			x = getattr(CLIENT, commands[0])(*args)
		# if x_find:
		# 	x = organizer_album_by_artist(x)
		# else:
		if x:
			if 'find' in commands:
				x = organizer_album_by_artist(x)
				navigator_find(x, host)
			elif 'list' in commands:
				x2 = []
				for i in x:
					x2.append(str(x.index(i)) + ". " + i)
				makeList(x2, n_list)
			else:
				print(x)
		# print("#"*cmdw3.getWidth())
	else:
		x = getattr(CLIENT, commands[0])()
		if x:
			print(x)
		# print("#"*cmdw3.getWidth())

def execute(host=None, commands=None):
	debug(commands=commands)
	if not commands:
		q = input('FUNCTION: ')
	else:
		q = commands
	if isinstance(q, list):
		q = " ".join(q)
	debug(commands_q=q)
	if "#" in q:
		list_command = str(q).strip().split("#")
		debug(list_command=list_command)
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


