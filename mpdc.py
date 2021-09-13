#!python

try:    
    from pause import pause
except:
    def pause(*args, **kwargs):
        q = input("Please enter to continue ...")
        return()
import os
from pprint import pprint
import sys
if sys.version_info.major == 2:
    input = raw_input
import mpd
import traceback
from configset import configset
import argparse

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

# print("HOST:", HOST)
# print("PORT:", PORT)
CLIENT = ''
ADD = False
FIRST = False
CALL_PLAYLIST = False
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
    debug(results = results)
    albums = []
    #paths = []
    album_paths = {}
    n = 0
    #debug(results = results)
    for i in results:
        #print ("i =",i)
        #debug(i = i)
        if isinstance(i, list):
            for x in i:
                albums.append((x.get('album'), x.get('artist'), x.get('disc'), os.path.dirname(x.get('file')), x.get('date')))
        else:		
            albums.append((i.get('album'), i.get('artist'), i.get('disc'), os.path.dirname(i.get('file')), i.get('date')))
        #paths.append(os.path.dirname(i.get(file)))
    debug(albums = albums)
    album = sorted(set(albums))
    debug(album = album)
    #album = albums
    # print("album =", album)
    for i in album:
        file_album_path = ''
        for x in results:
            if isinstance(x, list):
                for y in x:
                    if y.get('album') == i[0]:
                        album_paths.update(
                            {
                                n: {
                                    'album':i[0],
                                    'path':i[3],
                                    'artist':i[1],
                                    'year':i[4]
                                }
                            }
                        )
                        # n+=1
                        break		
            else:
                if x.get('album') == i[0]:
                    if not os.path.dirname(x.get('file')) == file_album_path:
                        file_album_path = os.path.dirname(x.get('file'))
                        n+=1
                    album_paths.update(
                        {
                        n: {
                            'album':i[0],
                            'artist':i[1],
                            # 'path':os.path.dirname(x.get('file')),
                            'path':i[3],
                            'year':i[4]
                        }
                    })
                        
        #break
        n+=1
    #print ("album_paths =", album_paths)
    return album_paths

def navigator_find(x, host=None, clear=True):
    # print ("x =", x)
    ADD = False
    play_root=False
    #multiplay=False
    def executor(q):
        q = int(q.strip()) - 1
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
                    # pause()
                    # print ("path 1 =",path)
                    command_execute('add %s'%(path))
                #if not multiplay:
                #if not ADD:
                    #command_execute('play')
    #debug(x = x)
    #pprint(x)
    for i in x:
        year = x.get(i).get('year')
        if not year:
            year = ''        
        print(str(i + 1) + ". " + make_colors("Album :", 'y') + " " + make_colors(x.get(i).get('album'), 'b', 'ly') + " " + make_colors("[" + year + "]", 'lw', 'm'))
        print(" "*len(str(i)) + "  " + make_colors("Artist:", 'lg') + " " + make_colors(x.get(i).get('artist'), 'b', 'lg', ['bold', 'italic']))
        print(" "*len(str(i)) + "  " + make_colors("Path  :", 'lc') + " " + make_colors(x.get(i).get('path'), 'lw', 'lr', ['bold', 'italic']))
        print("-----------------------" + ("-" * len(x.get(i).get('path'))) + "--")
    q = input(make_colors('Play Album or execute commands', 'b', 'ly') + ' ' + make_colors('[number: n1,n2,n4|n5|n7;n8,n10-n34][a] a = add only (no clear and play):', 'b', 'lg') + " ")
    if q:
        debug(ADD = ADD)
        if q[-1] == 'a':
            q = q[:-1]
            #global ADD
            ADD = True
        if clear and not ADD and str(q).isdigit():
            command_execute('clear', host)
        if "," in q or "|" in q or ";" in q:
            #multiplay=True
            q1 = re.split(",| |;|\|", q)
            debug(q1=q1)
            # print("q1 =", q1)
            q2 = []
            for i in q1:
                if "-" in i:
                    fr,to = re.split("-", i)
                    if fr.isdigit() and to.isdigit():
                        q2+= range(abs(int(fr.strip()) - 1), int(to.strip()) + 1)
                if not str(i).strip() == '':
                    q2.append(i)
                if str(i).strip() == '-1':
                    play_root=True
            for i in q2:
                executor(i)
            if not ADD:
                command_execute('play')
            # global ADD
            ADD = False
        else:
            if str(q).strip().isdigit():
                executor(q)
                if not ADD:
                    command_execute('play')
                # global ADD
                ADD = False
            else:
                return command_execute(q)
    #elif q and (" " in q or "," in q or "." in q or "|" in q or "-" in q):
    #    list_q = re.split(" |-|,|\|\.", q)
    #    list_q = [d.strip() for d in list_q]
    #    print("list_q =", list_q)
def format_current(playname, len_x):
    artist = playname.get('artist')
    albumartist = playname.get('albumartist')
    title = playname.get('title')
    album = playname.get('album')
    track = playname.get('track')
    year = playname.get('date')
    genre = playname.get('genre')
    disc = playname.get('disc')
    if not year:
        year = ''
    if disc:
        disc = "0" + disc
    else:
        disc = "01"
    try:
        duration = "%2.2f"%(float(playname.get('duration')) / 60)
    except TypeError:
        duration = ''
    #else:
        #print(traceback.format_exc())
    filename = playname.get('file')
    if len(str(track)) == 1:
        track = "0" + str(track)
    elif len(str(track)) == 1 and len(str(len_x)) == 3:
        track = "00" + str(track)                                
    elif len(str(track)) == 2 and len(str(len_x)) == 3:
        n = "0" + str(n)
    if title:
        return make_colors(artist, 'lw', 'bl') + " - " +\
               make_colors(album, 'lw', 'm') + "/" +\
               make_colors(albumartist, 'lw', 'm') + " " +\
               make_colors("(" + year + ")", 'b', 'lc') + "/" +\
               make_colors(disc, 'b', 'lg') + "/" +\
               make_colors(track, 'r', 'lw') + ". " +\
               make_colors(title, 'b', 'ly') + " [" +\
               make_colors(duration, 'b', 'lg') + "]" + " [" +\
               make_colors(os.path.splitext(filename)[1][1:].upper(), 'lw', 'r') +\
               "] [" +\
               make_colors("ID:" + str(playname.get('id')), 'b', 'lc') + "]"
    else:
        return ''
    

def format_playlist(playname, len_x):
    debug(playname = playname)
    # pause()
    error = False    
    disc = "01"
    year = ''
    if isinstance(playname, str):
        try:
            data = re.compile(r'file\: (?P<path>.*?)/(?P<artist>.*?)/(?P<album>.*?)/(?P<track>\d.)\. (?P<title>.*)')
            path, artist, album, track, title = data.match(playname).groups()
        except:
            error = True
        if error:
            try:
                data = re.compile(r'file\: (?P<artist>.*?) - (?P<album>.*?)/(?P<disc>.*?)/(?P<track>\d.*)\. (?P<title>.*)')
                artist, album, disc, track, title = data.match(playname).groups()
            except:
                #print("error:", traceback.format_exc())
                error = True
        if error:
            try:
                data = re.compile(r'file\: (?P<path>.*?)/(?P<artist>.*?) - (?P<album>.*?)\((?P<year>\d{4})\)/(?P<track>\d.)\. (?P<title>.*)', re.I)
                path, artist, album, year, track, title = data.match(playname).groups()
            except:
                #print("error:", traceback.format_exc())
                error = True            
        #print("PLAYNAME =", playname)
        #print("DATA =", data)
        #print("ARTIST:", artist)
        #print("ALBUM :", album)
        #print("DISC  :", disc)
        #print("TRACK :", track)
        #print("TITLE :", title)
        if not disc:
            disc = "01"
    elif isinstance(playname, dict):
        id = playname.get('id')
        artist = playname.get('artist')
        albumartist = playname.get('albumartist')
        title = playname.get('title')
        album = playname.get('album')
        track = playname.get('track')
        year = playname.get('date')
        genre = playname.get('genre')
        disc = playname.get('disc')
        if not disc:
            disc = "01"
        else:
            disc = "0" + playname.get('disc')
        duration = "%2.2f"%(float(playname.get('duration')) / 60)
        filename = playname.get('file')
        if len(str(track)) == 1:
            track = "0" + str(track)
        elif len(str(track)) == 1 and len(str(len_x)) == 3:
            track = "00" + str(track)                                
        elif len(str(track)) == 2 and len(str(len_x)) == 3:
            n = "0" + str(n)                                                        
        return make_colors(artist, 'lw', 'bl') + " - " +\
               make_colors(album, 'lw', 'm') + "/" +\
               make_colors(albumartist, 'lw', 'm') + " " +\
               make_colors("(" + year + ")", 'b', 'lc') + "/" +\
               make_colors(disc, 'b', 'lg') + "/" +\
               make_colors(track, 'r', 'lw') + ". " +\
               make_colors(os.path.splitext(title)[0], 'b', 'ly') + " [" +\
               make_colors(duration, 'b', 'lg') + "]" + " [" +\
               make_colors(os.path.splitext(filename)[1][1:].upper(), 'lw', 'r') +\
               "] [" + make_colors("ID:" + str(id), 'b', 'lc') + "]"
    if year:
        return make_colors(artist, 'lw', 'bl') + " - " + make_colors(album, 'lw', 'm') + " " + make_colors("(" + year + ")", 'b', 'lc') + "/" + make_colors(disc, 'b', 'lg') + "/" + make_colors(track, 'r', 'lw') + ". " + make_colors(os.path.splitext(title)[0], 'b', 'ly') + " [" + make_colors(os.path.splitext(title)[1][1:].upper(), 'lw', 'r') + "]"
    return make_colors(artist, 'lw', 'bl') + " - " + make_colors(album, 'lw', 'm') + "/" + make_colors(disc, 'b', 'lg') + "/" + make_colors(track, 'r', 'lw') + ". " + make_colors(os.path.splitext(title)[0], 'b', 'ly') + " [" + make_colors(os.path.splitext(title)[1][1:].upper(), 'lw', 'r') + "] [" + make_colors("ID:" + str(id), 'b', 'lc') + "]"

def command_execute(commands, host=None, port=None):
    global FIRST
    debug(commands = commands)
    debug(ADD = ADD)
    debug(host = host)
    debug(port = port)
    if not host:
        if config.get_config('server', 'host'):
            host = config.get_config('server', 'host')
        if os.getenv('MPD_HOST'):
            host = os.getenv('MPD_HOST')
    if not port:
        if config.get_config('server', 'port'):
            port = config.get_config('server', 'port')
        if os.getenv('MPD_PORT'):
            port = os.getenv('MPD_PORT')
    debug(host = host)
    debug(port = port)
    if not FIRST:
        print(make_colors("command_execute HOST:", 'lw', 'bl') + " " + make_colors(host, 'b', 'y'))
        print(make_colors("command_execute PORT:", 'lw', '1r') + " " + make_colors(str(port), 'b', 'lc'))
        FIRST = True
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
    elif 'add' in commands or 'remove' in commands or 'delete' in commands:
        commands = str(commands).strip().split(' ', 1)
    else:
        commands = str(commands).strip().split(' ')
    # print("commands tuple =", (tuple(commands[1:])))
    debug(commands = commands)
    for i in commands:
        if i[0] == 'N' and i[1].isdigit():
            n_list = int(i[1:])
            commands.remove(i)
    if not 'deleteid' == commands[0]:
        print("COMMAND :", " ".join(commands))
    debug(ADD = ADD)
    if len(commands) > 1:
        args = tuple(commands[1:])
        debug(args = args)
        debug(commands = commands)
        if 'play' in commands:
            if args[0].isdigit():
                args = [str(int(args[0].strip()) - 1)]
                print(make_colors("Playing track:", 'lw', 'bl') + " " + make_colors(str(int(args[0]) + 1), 'r', 'lw'))
                try:
                    x = getattr(CLIENT, commands[0])(*args)
                except:
                    print(make_colors("[play] Command Errors !", 'lw', 'r'))
                    return False
                try:
                    y = getattr(CLIENT, commands[0])(*args)
                except:
                    print(make_colors("[current song] Command Errors !", 'lw', 'r'))
                    return False
                if y:
                    if isinstance(y, dict):
                        for r in y:
                            fg, bg = setColor(random.choice(BG_COLORS))
                            print(make_colors(str(r).upper() + " " * (15 - len(r)), fg, bg) + make_colors(":", 'y') + " " + make_colors(str(y.get(r)), fg, bg))
                else:
                    if x:
                        print(x)
            else:
                print(make_colors("Failed to play number {}".format(args[0]), 'lw', 'r'))
        elif 'album' in commands and 'find' in commands:
            try:
                x = getattr(CLIENT, commands[0])(*args)
            except:
                print(make_colors("[album] Command Errors !", 'lw', 'r'))
                return False
            # debug(x = x)
            # pause()
            if not x:
                debug("not x")
                x = getattr(CLIENT, 'list')('album')
                debug(len_x = len(x))
                debug(commands_index_album_add = commands[commands.index('album') + 1].lower())
                x_find_album = []
                for i in x:
                    if commands[commands.index('album') + 1].lower() in str(i.get('album')).lower().strip():
                        debug(find = str(i.get('album')).lower().strip())
                        debug(patten = commands[commands.index('album') + 1].lower())
                        x1 = getattr(CLIENT, 'find')('album', i.get('album'))
                        debug(x1 = x1)
                        x_find_album.append(x1)
                        debug(x_find_album = x_find_album)
                x = x_find_album
                x_find = True
        elif 'artist' in commands and 'find' in commands:
            try:
                x = getattr(CLIENT, commands[0])(*args)
            except:
                print(make_colors("[artist] Command Errors !", 'lw', 'r'))
                return False
            if not x:
                debug("not x")
                x = getattr(CLIENT, 'list')('artist')
                # debug(x = x)
                # print ("XXX =", x)
                debug(len_x = len(x))
                debug(commands_index_album_add = commands[commands.index('artist') + 1].lower())
                x_find_artist = []
                for i in x:
                    if commands[commands.index('artist') + 1].lower() in str(i.get('artist')).lower().strip():
                        debug(find = str(i.get('artist')).lower().strip())
                        debug(patten = commands[commands.index('artist') + 1].lower())
                        x1 = getattr(CLIENT, 'find')('artist', i.get('artist'))
                        debug(x1 = x1)
                        x_find_artist.append(x1)
                        debug(x_find_artist = x_find_artist)
                x = x_find_artist
                x_find = True
                debug(x = x)
        elif 'playlist' in commands:
            global CALL_PLAYLIST
            CALL_PLAYLIST = True
            try:
                x = getattr(CLIENT, "playlistid")(*args)
            except:
                print(make_colors("[playlist] Command Errors !", 'lw', 'r'))
                return False
            debug(x = x)
            len_x = len(x)
            n = 1
            for i in x:
                if len(str(n)) == 1 and len(str(len_x)) == 2:
                    n = "0" + str(n)
                elif len(str(n)) == 1 and len(str(len_x)) == 3:
                    n = "00" + str(n)                                
                elif len(str(n)) == 2 and len(str(len_x)) == 3:
                    n = "0" + str(n)                                
                #print (str(n) + ". " + i)
                print (make_colors(str(n), 'bl') + ". " + format_playlist(i, len_x))
                n = int(n)
                n += 1
            qp = input(make_colors('Play musics', 'b', 'ly') + ' ' + make_colors('[number]:', 'b', 'lg') + " ")
            if qp:
                if qp.strip().isdigit() and int(qp.strip()) < len(x):
                    return command_execute(["play", str(int(qp.strip()))])
            
        elif 'delete' in commands or 'remove' in commands:
            all_numbers = []
            if len(commands) > 1:
                numbers = list(filter(None, re.split(" |,|#|\|", commands[1])))
                debug(numbers = numbers)
                if numbers:
                    for n in numbers:
                        if "-" in n:
                            num_range = re.split("-", n.strip())
                            debug(num_range = num_range)
                            num_range = list(range(int(num_range[0].strip()), int(num_range[1].strip()) + 1))
                            debug(num_range = num_range)
                            if num_range:
                                all_numbers += num_range
                            debug(all_numbers)
                        else:
                            all_numbers.append(n)
            all_numbers = list(set(sorted(all_numbers)))
            debug(all_numbers = all_numbers)
            
            if all_numbers:
                try:
                    x = getattr(CLIENT, "playlistid")()
                except:
                    print(make_colors("[delete] Error get list playlist !", 'lw', 'r'))
                    return False
                for nn in all_numbers:
                    command_execute("deleteid " + x[nn - 1].get('id'), host, port)
        else:
            try:
                x = getattr(CLIENT, commands[0])(*args)
            except:
                print(make_colors("[else] Command Errors !", 'lw', 'r'))
                return False                
        # if x_find:
        # 	x = organizer_album_by_artist(x)
        # else:
        try:
            if x:
                debug(x = x)
                if 'delete' in commands or 'remove' in commands:
                    command_execute("playlist")
                elif 'find' in commands:
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
        except:
            print(traceback.format_exc())
        # print("#"*cmdw.getWidth())
    else:
        if 'playlist' in commands:
            CALL_PLAYLIST = True
            x = getattr(CLIENT, "playlistid")()
            debug(x = x)
            len_x = len(x)
            n = 1
            for i in x:
                if len(str(n)) == 1:
                    n = "0" + str(n)
                elif len(str(n)) == 1 and len(str(len_x)) == 3:
                    n = "00" + str(n)                                
                elif len(str(n)) == 2 and len(str(len_x)) == 3:
                    n = "0" + str(n)                                                
                print (make_colors(str(n), 'bl') + ". " + format_playlist(i, len_x))
                n = int(n)
                n += 1
            currentsong = getattr(CLIENT, "currentsong")()
            print("-" * ((cmdw.getWidth() * 2) - 2))
            print(make_colors("current playing:", 'r', 'lw') + " " + format_current(currentsong, len_x))
            print("_" * ((cmdw.getWidth() * 2) - 2))
            qp = input(make_colors('Play musics of number or execute commands, [q]uit|e[x]it = quit/exit', 'b', 'ly') + ' ' + make_colors('[number]:', 'b', 'lg') + " ")
            if qp and str(qp).isdigit():
                if qp.strip().isdigit() and int(qp.strip()) < len(x):
                    return command_execute(["play", str(int(qp.strip()))])
                else:
                    return command_execute(qp)
            elif qp == 'x' or qp == 'q' or qp == 'exit' or qp == 'quit':
                sys.exit()
            else:
                sys.exit()
        elif 'next' in commands or 'prev' in commands:
            x = getattr(CLIENT, commands[0])()
            debug(x = x)
            len_x = 1
            if x:
                len_x = len(x)
            currentsong = getattr(CLIENT, "currentsong")()
            print("[" + make_colors(commands[0], 'b', 'y') + "] " + make_colors("now is playing:", 'r', 'lw') + " " + format_current(currentsong, len_x))
        elif 'listplaylists' in commands:
            x = getattr(CLIENT, commands[0])()
            debug(x = x)
            len_x = 1
            n = 1
            if x and isinstance(x, list):
                len_x = len(x)
                for i in x:
                    if len(str(n)) == 1:
                        n = "0" + str(n)
                    elif len(str(n)) == 1 and len(str(len_x)) == 3:
                        n = "00" + str(n)                                
                    elif len(str(n)) == 2 and len(str(len_x)) == 3:
                        n = "0" + str(n)                                                
                    print (make_colors(str(n), 'bl') + ". " + make_colors(i.get('playlist'), 'b', 'y') + " [" + make_colors(i.get('last-modified'), 'lw', 'm') + "]")
                print("\n")
        else:
            debug(commands = commands)
            x = getattr(CLIENT, commands[0])()
            if x:
                if isinstance(x, dict):
                    for r in x:
                        fg, bg = setColor(random.choice(BG_COLORS))
                        print(make_colors(str(r).upper() + " " * (15 - len(r)), fg, bg) + make_colors(":", 'y') + " " + make_colors(str(x.get(r)), fg, bg))
                elif isinstance(x, list):
                    for r in x:
                        if isinstance(r, dict):
                            for a in r:
                                fg, bg = setColor(random.choice(BG_COLORS))
                                print(make_colors(str(a).upper() + " " * (15 - len(a)), fg, bg) + make_colors(":", 'y') + " " + make_colors(str(r.get(a)), fg, bg))
                            print("-" * cmdw.getWidth())
                else:
                    print(x)
            # print("#"*cmdw.getWidth())
    if CALL_PLAYLIST:
        try:
            command_execute("playlist", host, port)
        except:
            pass
        

def execute(host=None, port=None, commands=None):
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
        if "add" in list_command:
            global ADD
            ADD = True
            list_command.remove('add')
        debug(ADD = ADD)
        debug(list_command=list_command)
        debug(ADD = ADD)
        for i in list_command:
            command_execute(str(i).strip(), host, port)
    else:
        command_execute(q, host, port)

def usage():
    usage_txt = """mpdc.py [-h] [-H HOST] [-P PORT] [COMMANDS ...]

    positional arguments:
      COMMANDS              Commands, example: find artist coldplay"""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, usage = usage_txt)
    parser.add_argument('-H', '--host', action='store', help='MPD HOST, default: 127.0.0.1', default='127.0.0.1', type=str)
    parser.add_argument('-P', '--port', action='store', help='MPD PORT, default: 6600', default=6600, type=int)
    #parser.add_argument("COMMANDS", action='store', help="Commands", nargs='*')
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n")
        print("MPD_HOST (Environment): ", os.getenv('MPD_HOST'))
        execute(None, None, ["playlist"])
    else:
        direct = False
        args = sys.argv[1:]
        debug(args = args)
        
        for i in args:
            if i == '-P' or i == '--port':
                PORT = args[args.index(i) + 1]
                if not PORT.isdigit():
                    PORT = ''
                args.remove(i)
                args.remove(args[args.index(PORT)])
                debug(PORT = PORT)
                debug(args = args)
        for i in args:
            if i == '-H' or i == '--host':
                HOST = args[args.index(i) + 1]
                if not len(HOST.split(".")) == 4:
                    HOST = ''
                args.remove(i)
                args.remove(args[args.index(HOST)])
                debug(HOST = HOST)

        debug(args = args)
        if len(args) > 0:
            parser.add_argument("COMMANDS", action='store', help="Commands", nargs='*')
            args = parser.parse_args()
            PORT = args.port
            HOST = args.host
            if HOST:
                os.environ.update({'MPD_HOST': HOST,})
            if PORT:
                os.environ.update({'MPD_PORT': str(PORT),})
            execute(args.host, args.port, args.COMMANDS)
        else:
            os.environ.update({"HOST": HOST,})
            os.environ.update({"PORT": PORT,})
            execute(HOST, PORT, ["playlist"])

if __name__ == '__main__':
    print("PID : ", os.getpid())
    usage()
    # print("MPD_HOST (Environment): ", os.getenv('MPD_HOST'))
    # print("len(sys.argv) =", len(sys.argv))
    # if len(sys.argv) == 2:
    #     if len(str(sys.argv[1]).strip().split(".")) == 4:
    #         execute(host=sys.argv[1])
    #     else:
    #         execute(commands=sys.argv[1:])
    # elif len(sys.argv) > 2:
    #     if len(str(sys.argv[1]).strip().split(".")) == 4:
    #         #print("sys.argv[2:] =", sys.argv[2:]) 
    #         execute(host=sys.argv[1], commands=sys.argv[2:])
    #     else:
    #         # print("sys.argv[1:] =", sys.argv[1:])
    #         execute(commands=sys.argv[1:])		

    # else:
    #     execute()



