#!python
import os
import sys
if sys.version_info.major == 2:
    input = raw_input
import mpd
import traceback
from configset import configset

HOST = '127.0.0.1'
configname = os.path.join(os.path.relpath(os.path.dirname(__file__)), 'mpdc.ini')
config = configset(configname)
#config.configname = configname
if config.read_config('server', 'host', value = '127.0.0.1'):
    HOST = config.read_config('server', 'host', value = '127.0.0.1')
if config.read_config('server', 'port', value = '6600'):
    PORT = config.read_config('server', 'host', value = '6600')
    if PORT and str(PORT).isdigit():
        PORT = int(PORT)
    else:
        PORT = 6600
if os.getenv('MPD_HOST'):
    HOST = os.getenv('MPD_HOST')
else:
    HOST = '127.0.0.1'
if os.getenv('MPD_PORT'):
    PORT = os.getenv('MPD_PORT')
else:
    PORT = '6600'

print("HOST:", HOST)
print("PORT:", PORT)
CLIENT = ''
import time
import cmdw
from pydebugger.debug import debug
from make_colors import make_colors
import re
import random

BG_COLORS = ['r', 'bl', 'lg', 'c', 'y', 'lm', 'lb', 'g', 'lg', 'ly', 'm']

def setColor(bg):
    if bg == 'y' or bg == 'ly' or bg == 'yellow' or bg == 'lightyellow':
        fg = 'b'
    elif bg == 'c' or bg == 'lc' or bg == 'cyan' or bg == 'lightcyan':
        fg = 'b'
    elif bg == 'g' or bg == 'lg' or bg == 'green' or bg == 'lightgreen':
        fg = 'b'
    else:
        fg = 'lw'
    return fg, bg

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


def conn(host=None, port=6600, max_try=10):
    global HOST
    global PORT
    CLIENT = ''
    error = False
    nt = 0
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
            tp, vl, tr = sys.exc_info()
            print(make_colors("Try:", 'lw', 'bl') + " " + make_colors(str(nt), 'b', 'y'))
            print("     Type traceback:", make_colors(vl.__class__.__name__, 'lw', 'r'))
            print("     Msg  traceback:", make_colors(vl.args, 'b', 'g'))
            if str(vl.__class__.__name__) == 'OSError' and "No route to host" in vl.args:
                print(make_colors("CaNot Connected !, maybe host is down !", 'lw', 'r'))
                break
            if nt < max_try:
                nt+=1
            else:
                print(make_colors("Can't connect to {}:{} !".format(HOST, PORT), 'lw', 'lr'))
                error = True
                break
            time.sleep(0.03)
    if error:
        sys.exit()
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
    # print ("album_paths =", album_paths)
    return album_paths

def navigator_find(x, host=None, clear=True):
    # print ("x =", x)
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
        print(str(i) + ". " + "Album: " + make_colors(x.get(i).get('album'), 'b', 'ly'))
        print(" "*len(str(i)) + "  " + "Path : " + make_colors(x.get(i).get('path'), 'lw', 'lr', ['bold', 'italic']))
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
    if config.get_config('server', 'host'):
        host = config.get_config('server', 'host')
    if config.get_config('server', 'port'):
        port = config.get_config('server', 'port')
    if os.getenv('MPD_HOST'):
        host = os.getenv('MPD_HOST')
    if os.getenv('MPD_PORT'):
        port = os.getenv('MPD_PORT')
    debug(host = host)
    debug(port = port)
    print(make_colors("command_execute HOST:", 'lw', 'bl') + " " + make_colors(host, 'b', 'y'))
    print(make_colors("command_execute PORT:", 'lw', '1r') + " " + make_colors(str(port), 'b', 'lc'))
    n_list = 10
    x_find = False
    #debug('commands_execute')
    if isinstance(commands, list):
        commands = " ".join(commands)
    CLIENT = conn(host, port)
    debug(CLIENT = CLIENT)
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
        debug(args = args)
        debug(commands = commands)
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
        elif 'artist' in commands and 'find' in commands:
            x = getattr(CLIENT, commands[0])(*args)
            if not x:
                debug("not x")
                x = getattr(CLIENT, 'list')('artist')
                # print ("XXX =", x)
                debug(len_x = len(x))
                debug(commands_index_album_add = commands[commands.index('artist') + 1].lower())
                x_find_artist = []
                for i in x:
                    if commands[commands.index('artist') + 1].lower() in str(i).lower():
                        x1 = getattr(CLIENT, 'find')('artist', i)
                        x_find_artist.append(x1)
                x = x_find_artist
                # print ("XXX =", x)
                x_find = True
        elif 'playlist' in commands:
            x = getattr(CLIENT, commands[0])()
            len_x = len(x)
            n = 1
            for i in x:
                if len(str(n)) == 1 and len(str(len_x)) == 2:
                    n = "0" + str(n)
                elif len(str(n)) == 1 and len(str(len_x)) == 3:
                    n = "00" + str(n)                                
                elif len(str(n)) == 2 and len(str(len_x)) == 3:
                    n = "0" + str(n)                                
                print (str(n) + ". " + i)
                n = int(n)
                n += 1
        else:
            x = getattr(CLIENT, commands[0])(*args)
        # if x_find:
        # 	x = organizer_album_by_artist(x)
        # else:
        if x:
            debug(x = x)
            if 'find' in commands:
                x = organizer_album_by_artist(x)
                debug(x = x)
                # sys.exit()
                navigator_find(x, host)
            elif 'list' in commands:
                x2 = []
                for i in x:
                    if isinstance(i, dict):
                        if i.get('artist'):
                            x2.append(str(x.index(i)) + ". " + i.get('artist'))        
                    else:
                        x2.append(str(x.index(i)) + ". " + i)
                    
                makeList(x2, n_list)
            else:
                if isinstance(x, dict):
                    for r in x:
                        print(r + ": " + x.get(r))
                else:
                    print(x)
        # print("#"*cmdw.getWidth())
    else:
        if 'playlist' in commands:
            x = getattr(CLIENT, commands[0])()
            len_x = len(x)
            n = 1
            for i in x:
                if len(str(n)) == 1:
                    n = "0" + str(n)
                elif len(str(n)) == 1 and len(str(len_x)) == 3:
                    n = "00" + str(n)                                
                elif len(str(n)) == 2 and len(str(len_x)) == 3:
                    n = "0" + str(n)                                                
                print (str(n) + ". " + i)
                n = int(n)
                n += 1
        else:
            x = getattr(CLIENT, commands[0])()
            if x:
                if isinstance(x, dict):
                    for r in x:
                        fg, bg = setColor(random.choice(BG_COLORS))
                        print(make_colors(str(r).upper() + " " * (15 - len(r)), fg, bg) + make_colors(":", 'y') + " " + make_colors(str(x.get(r)), fg, bg))
                else:
                    print(x)
            # print("#"*cmdw.getWidth())

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
    print("PID : ", os.getpid())
    print("MPD_HOST (Environment): ", os.getenv('MPD_HOST'))
    #print("len(sys.argv) =", len(sys.argv))
    if len(sys.argv) == 2:
        if len(str(sys.argv[1]).strip().split(".")) == 4:
            execute(host=sys.argv[1])
        else:
            execute(commands=sys.argv[1:])
    elif len(sys.argv) > 2:
        if len(str(sys.argv[1]).strip().split(".")) == 4:
            #print("sys.argv[2:] =", sys.argv[2:]) 
            execute(host=sys.argv[1], commands=sys.argv[2:])
        else:
            # print("sys.argv[1:] =", sys.argv[1:])
            execute(commands=sys.argv[1:])		

    else:
        execute()



