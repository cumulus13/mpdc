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
import time
import cmdw
from pydebugger.debug import debug
from make_colors import make_colors
import re
import random

class MPDC(object):
    HOST = ''
    PORT = ''
    configname = os.path.join(os.path.relpath(os.path.dirname(__file__)), 'mpdc.ini')
    config = configset(configname)
    #config.configname = configname
    CLIENT = ''
    ADD = False
    FIRST = False
    CALL_PLAYLIST = False
    BG_COLORS = ['r', 'bl', 'lg', 'c', 'y', 'lm', 'lb', 'g', 'lg', 'ly', 'm']
    diplay_columns = ''
    stations = ''
    CLIENT = None
    
    def __init__(self, host = None, port = None, configfile = None):
        super(MPDC, self).__init__()
        self.HOST = host or self.HOST
        self.PORT = port or self.PORT
        self.config.configname = configfile or self.config.configname

    @classmethod
    def ver_host(self, host = None, port = None):
        if self.HOST and self.PORT:
            return self.HOST, self.PORT
        debug(host = host)
        debug(port = port)
        #pause()
        if not host:
            if os.getenv('MPD_HOST'):
                host = os.getenv('MPD_HOST')
        if not port:
            if os.getenv('MPD_PORT'):
                port = os.getenv('MPD_PORT')
        if not host:
            if self.config.read_config('server', 'host', value = '127.0.0.1'):
                host = self.config.read_config('server', 'host', value = '127.0.0.1')
        if not port:
            if self.config.read_config('server', 'port', value = '6600'):
                port = self.config.read_config('server', 'host', value = '6600')
                if port and str(port).isdigit():
                    port = int(port)
                else:
                    port = 6600
        
        host = host or '127.0.0.1'
        port = port or 6601
        debug(host = host)
        debug(port = port)
        #pause()
        if not self.HOST:
            self.HOST = host
        if not self.PORT:
            self.PORT = port
        return host, port
    
    @classmethod
    def setColor(self, bg):
        if bg == 'y' or bg == 'ly' or bg == 'yellow' or bg == 'lightyellow':
            fg = 'b'
        elif bg == 'c' or bg == 'lc' or bg == 'cyan' or bg == 'lightcyan':
            fg = 'b'
        elif bg == 'g' or bg == 'lg' or bg == 'green' or bg == 'lightgreen':
            fg = 'b'
        else:
            fg = 'lw'
        return fg, bg
    
    @classmethod
    def makeList(self, alist, ncols, vertically=True, file=None):
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
    
    @classmethod
    def conn0(self, host=None, port=None, playlist="radio", columns=200):
        mpd_host = self.HOST
        mpd_port = self.PORT
        self.diplay_columns = columns
        mpd_client = mpd.MPDClient()
        mpd_client.timeout = 20
        mpd_client.idletimeout = None
        mpd_client.connect(mpd_host, mpd_port)
        return mpd_client
    
    @classmethod
    def hostport_confirm(self, host = None, port = None):
        return self.ver_host(host, port)
    
    @classmethod
    def conn(self, host=None, port=None, max_try=10):
        host, port = self.ver_host(host, port)
        error = False
        nt = 0
        mpd_client = mpd.MPDClient()
        while 1:
            try:
                debug(host = host)
                debug(port = port)
                mpd_client.connect(host=host, port=port)
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
                    print(make_colors("Can't connect to {}:{} !".format(host, port), 'lw', 'lr'))
                    error = True
                    break
                time.sleep(0.03)
        if error:
            sys.exit()
        mpd_client.timeout = 20
        mpd_client.idletimeout = None
        return mpd_client
    
    @classmethod
    def organizer_album_by_artist(self, results, albumartist = False):
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
                    album = x.get('album') or ''
                    if albumartist:
                        artist = x.get('albumartist') or ''
                    else:
                        artist = x.get('artist') or ''
                    disc = x.get('disc') or ''
                    file = x.get('file') or ''
                    if file:
                        file = os.path.dirname(x.get('file'))
                    date = x.get('date') or ''
                    if albumartist:
                        albums.append((album, artist, disc, file, date))
                    else:
                        albums.append((album, artist, disc, file, date))
            else:	
                album = i.get('album') or ''
                artist = i.get('artist') or ''
                disc = i.get('disc') or ''
                file = i.get('file') or ''
                if file:
                    file = os.path.dirname(i.get('file'))
                date = i.get('date') or ''            
                albums.append((album, artist, disc, file, date))
            #paths.append(os.path.dirname(i.get(file)))
        debug(albums = albums)
        try:
            album = sorted(set(albums))
        except:
            debug(albums = albums)
            album = []
            album_str = ''
            for ab in albums:
                if not album_str == ab[3]:
                    album.append(ab)
                    album_str = ab[3]
            try:
                album = sorted(album)
            except:
                #pause()
                album = albums
                print(traceback.format_exc())
            
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

    @classmethod
    def format_number(self, number, length = 10):
        number = str(number).strip()
        if not str(number).isdigit():
            return number
        zeros = len(str(length)) - len(number)
        r = ("0" * zeros) + str(number)
        if len(r) == 1:
            return "0" + r
        return r
    
    @classmethod
    def organizer_album_by_title(self, results, sort_by='title'):
        # print ("results =", results[1])
        error_sort = False
        debug(results = results)
        # pause()
        try:
            results = sorted(results, key=lambda k: k.get('title'))
        except:
            error_sort = True
            results = sorted(results, key=lambda k: re.split("^\d\+. |^\d+ - ", os.path.basename(k.get('file')))[-1])

        if not error_sort and sort_by == 'file':
            results = sorted(results, key=lambda k: re.split("^\d\+. |^\d+ - ", os.path.basename(k.get('file')))[-1])
                    
        song_paths = {}
        n = 0
        for i in results:
            # all_songs.append((file, album, artist, disc, date))
            song_paths.update(
                {
                    n: {
                            'album':i.get('album'),
                            'artist':i.get('artist'),
                            # 'path':os.path.dirname(x.get('file')),
                            'path':i.get('file'),
                            'year':i.get('date')
                        }
                }
            )
            n+=1
        #print ("song_paths =", song_paths)
        return song_paths
    
    @classmethod
    def navigator_find(self, x, host=None, port = None, clear=True, q = None):
        ADD_ALL = False
        debug(x = x)
        # pause()
        host = host or self.hostport_confirm(host, port)[0]
        port = port or self.hostport_confirm(host, port)[1]
        debug(host = host)
        debug(port = port)
        listit = False
        
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
                        self.command_execute('add %s'%(path))
                    else:
                        path = x.get(int(q)).get('path')
                        debug(path=path)
                        # #pause()
                        # print ("path 1 =",path)
                        self.command_execute('add %s'%(path))
                    #if not multiplay:
                    #if not ADD:
                        #command_execute('play')
        #debug(x = x)
        #pprint(x)
        if not q:
            for i in x:
                year = x.get(i).get('year')
                if not year:
                    year = ''
                if isinstance(year, list):
                    year = list(filter(None, year))
                    year = list(set(year))
                    year = year[0]
                album = x.get(i).get('album') or ''
                artist = x.get(i).get('artist') or ''
                path = x.get(i).get('path') or ''
                debug(year = year)
                debug(album = album)
                debug(artist = artist)
                debug(path = path)
                
                print(str(i + 1) + ". " + make_colors("Album :", 'y') + " " + make_colors(album, 'b', 'ly') + " " + make_colors("[" + year + "]", 'lw', 'm'))
                print(" "*len(str(i)) + "  " + make_colors("Artist:", 'lg') + " " + make_colors(x.get(i).get('artist'), 'b', 'lg', ['bold', 'italic']))
                print(" "*len(str(i)) + "  " + make_colors("Path  :", 'lc') + " " + make_colors(x.get(i).get('path'), 'lw', 'lr', ['bold', 'italic']))
                print("-----------------------" + ("-" * len(x.get(i).get('path'))) + "--")
            q = input(make_colors('Play Album or execute commands', 'b', 'ly') + ' ' + make_colors('[number: n1,n2,n4|n5|n7;n8,n10-n34][a] a = add only (no clear and play):', 'b', 'lg') + " ")
        if q:
            if q[-1] == 'a' and q[:-1].isdigit():
                q = q[:-1]
                self.ADD = True
            elif q == 'a':
                ADD_ALL = True
            elif q[-1] == 'l' and q[:-1].isdigit():
                q = q[:-1]
                listit = True
        if q and q.isdigit():
            if clear and not self.ADD and str(q).isdigit() and not listit:
                self.command_execute('clear', host)
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
                if not self.ADD:
                    self.command_execute('play')
                # global ADD
                self.ADD = False
            elif listit:
                debug(x = x)
                # data = x.get(int(q.strip()) - 1)
                # debug(data = data)
                path = x.get(int(q.strip()) - 1).get('path')
                debug(path = path)
                args = (path, )
                data = self.re_execute("listall", args, None, host, port)
                debug(data = data)
                xdata = {}
                n = 0
                # pprint(data)
                debug(test = [d.get('file') for d in data[1:]])
                debug(test_max = max([d.get('file') for d in data[1:]]))
                # pause()
                print(make_colors("PATH:", 'y') + " " + make_colors(data[0].get('directory'), 'lw', 'm') + " :")
                for i in data[1:]:
                    xdata.update({n: {'path':i.get('file')}})
                    n+= 1
                    print(" "*4 + make_colors(self.format_number(n), 'lc') + ". " + make_colors(os.path.basename(i.get('file')), 'lw', 'bl', ['bold', 'italic']))
                print("-"*len(os.path.basename(max([d.get('file') for d in data[1:]]))))
                qp = input(make_colors('Play Song or execute commands', 'b', 'ly') + ' ' + make_colors('[number: n1,n2,n4|n5|n7;n8,n10-n34][a] a = add only (no clear and play):', 'b', 'lg') + " ")
                if qp:
                    return self.navigator_find(xdata, host, port, clear, qp)
            else:
                if str(q).strip().isdigit():
                    executor(q)
                    if not self.ADD:
                        self.command_execute('play')
                    # global ADD
                    self.ADD = False
                    try:
                        self.command_execute("playlist", host, port)
                    except:
                        print(traceback.format_exc())
                        pass
                else:
                    return self.command_execute(q)
        #elif q and (" " in q or "," in q or "." in q or "|" in q or "-" in q):
        #    list_q = re.split(" |-|,|\|\.", q)
        #    list_q = [d.strip() for d in list_q]
        #    print("list_q =", list_q)
        elif q == 'x' or q == 'q' or q == 'exit' or q == 'quit':
            pass
        elif ADD_ALL:
            for i in x:
                executor(str(i + 1))
            try:
                self.command_execute("playlist", host, port)
            except:
                print(traceback.format_exc())
                pass
        else:
            if q:
                return self.command_execute(q)
                
    @classmethod
    def format_current(self, playname, len_x):
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
            track = "0" + str(track)
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
        
    @classmethod
    def format_playlist(self, playname, len_x):
        debug(playname = playname)
        # #pause()
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
            debug(playname = playname)
            id = playname.get('id')
            artist = playname.get('artist')
            albumartist = playname.get('albumartist')
            title = playname.get('title')
            album = playname.get('album')
            track = playname.get('track')
            year = playname.get('date')
            if not year:
                year = ''
            genre = playname.get('genre')
            disc = playname.get('disc')
            if not disc:
                disc = "01"
            else:
                disc = "0" + playname.get('disc')
            try:
                duration = "%2.2f"%(float(playname.get('duration')) / 60)
            except:
                duration = ''
            filename = playname.get('file')
            debug(title = title)
            if not title:
                title = ''
            if len(str(track)) == 1:
                track = "0" + str(track)
            elif len(str(track)) == 1 and len(str(len_x)) == 3:
                track = "00" + str(track)                                
            elif len(str(track)) == 2 and len(str(len_x)) == 3:
                track = "0" + str(track)                                                        
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
    
    @classmethod
    def command_execute(self, commands, host=None, port=None):
        debug(commands = commands)
        debug(ADD = self.ADD)
        host, port = self.hostport_confirm(host, port)
        debug(host = host)
        debug(port = port)
        #pause()
        if not self.FIRST:
            print(make_colors("command_execute HOST:", 'lw', 'bl') + " " + make_colors(host, 'b', 'y'))
            print(make_colors("command_execute PORT:", 'lw', '1r') + " " + make_colors(str(port), 'b', 'lc'))
            self.FIRST = True
        n_list = 10
        x_find = False
        #debug('commands_execute')
        if isinstance(commands, list):
            commands = " ".join(commands)
        CLIENT = self.conn(host, port)
        debug(CLIENT = CLIENT)
        debug(commands=commands)
        if 'album' in commands or 'find' in commands:
            commands = str(commands).strip().split(' ', 2)
        elif 'add' in commands or 'remove' in commands or 'delete' in commands or 'update' in commands:
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
        debug(ADD = self.ADD)
        x = ''
        if len(commands) > 1:
            args = tuple(commands[1:])
            debug(args = args)
            debug(commands = commands)
            if 'play' in commands:
                if args[0].isdigit():
                    y = None
                    x = None
                    args = [str(int(args[0].strip()) - 1)]
                    print(make_colors("Playing track:", 'lw', 'bl') + " " + make_colors(str(int(args[0]) + 1), 'r', 'lw'))
                    try:
                        x = getattr(CLIENT, commands[0])(*args)
                    except:
                        print(make_colors("[play] Command Errors !", 'lw', 'r'))
                        if not self.CALL_PLAYLIST:    
                            return False
                    try:
                        y = getattr(CLIENT, commands[0])(*args)
                    except:
                        print(make_colors("[current song] Command Errors !", 'lw', 'r'))
                        if not self.CALL_PLAYLIST:
                            return False
                    if y:
                        if isinstance(y, dict):
                            for r in y:
                                fg, bg = self.setColor(random.choice(self.BG_COLORS))
                                print(make_colors(str(r).upper() + " " * (15 - len(r)), fg, bg) + make_colors(":", 'y') + " " + make_colors(str(y.get(r)), fg, bg))
                    else:
                        if x:
                            print(x)
                        if y:
                            print(y)
                else:
                    print(make_colors("Failed to play number {}".format(args[0]), 'lw', 'r'))
            if 'find' in commands:
                if ('album' in commands and 'find' in commands) or 'albumartist' in commands and 'find' in commands:
                    try:
                        x = getattr(CLIENT, commands[0])(*args)
                    except:
                        try:
                            x = self.re_execute(commands, args, host = host, port = port)
                        except:
                            print(make_colors("[album] Command Errors !", 'lw', 'r'))
                            if not self.CALL_PLAYLIST:
                                return False
                    debug(x = x)
                    # pause()
                    if not x:
                        debug("not x")
                        debug(join_commands = " ".join(commands))
                        album_str = re.findall('find (album.*?) ', " ".join(commands))[0]
                        debug(album_str = album_str)
                        # x = getattr(CLIENT, 'list')(album_str)
                        # def re_execute(self, command, args = (), CLIENT = None, host = None, port = None):
                        x = self.re_execute('list', (album_str), host = host, port = port)
                        debug(len_x = len(x))
                        debug(commands_index_album_add = commands[commands.index(album_str) + 1].lower())
                        x_find_album = []
                        for i in x:
                            if commands[commands.index(album_str) + 1].lower() in str(i.get(album_str)).lower().strip():
                                debug(find = str(i.get(album_str)).lower().strip())
                                debug(patten = commands[commands.index(album_str) + 1].lower())
                                x1 = getattr(CLIENT, 'find')(album_str, i.get(album_str))
                                debug(x1 = x1)
                                x_find_album.append(x1)
                                debug(x_find_album = x_find_album)
                        x = x_find_album
                        x_find = True
                elif ('title' in commands and 'find' in commands) or ('song' in commands and 'find' in commands) or ('composer' in commands and 'find' in commands):
                    debug(commands = commands)
                    all_songs = []
                    if "song" in commands:
                        index = commands.index("song")
                        commands.remove("song")
                        commands.insert(index, "title")
                    args = list(args)
                    if "song" in args:
                        index = args.index("song")
                        args.remove("song")
                        args.insert(index, "title")
                    args = tuple(args)
                    debug(commands = commands)
                    debug(args = args)
                    #pause()
                    try:
                        x = getattr(CLIENT, commands[0])(*args)
                    except:
                        print(make_colors("[album] Command Errors !", 'lw', 'r'))
                        if not self.CALL_PLAYLIST:
                            return False
                    debug(x = x)
                    # #pause()
                    if not x:
                        debug("not x")
                        all_songs = []
                        pattern = [commands[-1].capitalize(), commands[-1].title(), commands[-1].upper()]
                        debug(patten = pattern)
                        for i in pattern:
                            debug(i = i)
                            args = list(args)
                            args.remove(args[-1])
                            args.insert(1, i)
                            args = tuple(args)
                            debug(args = args)
                            try:
                                # x = getattr(CLIENT, 'find')(*args)
                                x = self.re_execute('find', args, CLIENT, host, port)
                                debug(x = x)
                                # print ("XXX =", x)
                            except:
                                print(traceback.format_exc())
                            if x:
                                all_songs = all_songs + x
                    debug(all_songs = all_songs)
                    # pause()
                    if all_songs:
                        x = all_songs
                
                elif 'artist' in commands and 'find' in commands:
                    try:
                        x = getattr(CLIENT, commands[0])(*args)
                        debug(x = x)
                    except:
                        print(make_colors("[artist] Command Errors !", 'lw', 'r'))
                        if not self.CALL_PLAYLIST:
                            return False
                    if not x:
                        debug("not x")
                        #pause()
                        try:
                            x = getattr(CLIENT, 'list')('artist')
                        except:
                            x = self.re_execute('list', ('artist'), None, host, port)
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
                else:
                    args = list(args)
                    if not 'any' in args:
                        args.insert(0, 'any')
                        args = tuple(args)
                    try:
                        debug(args = args)
                        x = getattr(CLIENT, commands[0])(*args)
                        debug(x = x)
                    except:
                        print(make_colors("[{}] Command Errors !".format(commands[0]), 'lw', 'r'))
                        if not self.CALL_PLAYLIST:
                            return False
                    if not x:
                        debug("not x")
                        all_founds = []
                        pattern = [commands[-1].capitalize(), commands[-1].title(), commands[-1].upper()]
                        for i in pattern:
                            debug(i = i)
                            args = list(args)
                            args.remove(args[-1])
                            args.insert(1, i)
                            args = tuple(args)
                            debug(args = args)
                            try:
                                x = getattr(CLIENT, 'find')(*args)
                                debug(x = x)
                                # print ("XXX =", x)
                            except:
                                print(traceback.format_exc())
                            if x:
                                all_founds += x
                    debug(all_founds = all_founds)
                    #pause()
                    if all_founds:
                        x = all_founds
            elif 'playlist' in commands:
                if 'playlist' in commands:
                    self.CALL_PLAYLIST = True            
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
                    print (make_colors(str(n), 'bl') + ". " + self.format_playlist(i, len_x))
                    n = int(n)
                    n += 1
                qp = input(make_colors('Play musics', 'b', 'ly') + ' ' + make_colors('[number]:', 'b', 'lg') + " ")
                if qp and qp.isdigit():
                    if qp.strip().isdigit() and int(qp.strip()) < len(x):
                        # self.command_execute(["play", str(int(qp.strip()))])
                        en = 0
                        en_max = 10
                        while 1:
                            try:
                                x = getattr(CLIENT, "play")(str(int(qp.strip()) - 1),)
                                break
                            except:
                                if not en == en_max:
                                    en+=1
                                    CLIENT = self.conn(host, port)
                                else:
                                    print(make_colors("ERROR Play track:", 'lw', 'r') + " " + make_colors(qp, 'lw', 'bl'))
                                    time.sleep(1)
                                    print("ERROR:", traceback.format_exc())
                                    break
                        return self.command_execute('playlist')
                elif qp == 'x' or qp == 'q' or qp == 'exit' or qp == 'quit':
                    sys.exit()
                else:
                    if qp:
                        self.command_execute(qp)
                        return self.command_execute('playlist')
                    else:
                        #sys.exit()
                        return self.command_execute('playlist')
            elif 'delete' in commands or 'remove' in commands or 'del' in commands or 'rm' in commands:
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
                                all_numbers.append(int(n))
                debug(all_numbers = all_numbers)
                all_numbers = list(set(sorted(all_numbers)))
                debug(all_numbers = all_numbers)
                #pause()
                if all_numbers:
                    try:
                        x = getattr(CLIENT, "playlistid")()
                    except:
                        print(make_colors("[delete] Error get list playlist !", 'lw', 'r'))
                        if not self.CALL_PLAYLIST:
                            return False
                    debug(all_numbers = all_numbers)
                    for nn in all_numbers:
                        #command_execute("deleteid " + x[nn - 1].get('id'), host, port)
                        try:
                            getattr(CLIENT, "deleteid")(x[int(nn) - 1].get('id'))
                        except:
                            CLIENT = self.conn(host, port)
                            getattr(CLIENT, "deleteid")(x[int(nn) - 1].get('id'))
            else:
                try:
                    x = getattr(CLIENT, commands[0])(*args)
                except:
                    print(traceback.format_exc())
                    print(make_colors("[else] Command Errors !", 'lw', 'r'))
                    if not self.CALL_PLAYLIST:
                        return False                
            
            try:
                if x:
                    debug(x = x)
                    if 'delete' in commands or 'remove' in commands or 'del' in commands or 'rm' in commands:
                        self.command_execute("playlist")
                    elif 'find' in commands:
                        debug(commands = commands)
                        # pause()
                        if 'title' in commands:
                            x = self.organizer_album_by_title(x)
                        elif 'artist' in commands or 'albumartist' in commands or 'album' in commands:
                            if 'albumartist' in commands:
                                x = self.organizer_album_by_artist(x, True)
                            else:
                                x = self.organizer_album_by_artist(x)
                        else:
                            x = self.organizer_album_by_title(x, 'file')
                            debug(x = x)
                        # sys.exit()
                        self.navigator_find(x, host, port)
                    elif 'list' in commands:
                        x2 = []
                        for i in x:
                            if isinstance(i, dict):
                                if i.get('artist'):
                                    x2.append(str(x.index(i)) + ". " + i.get('artist'))        
                            else:
                                x2.append(str(x.index(i)) + ". " + i)
                            
                        self.makeList(x2, n_list)
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
                self.CALL_PLAYLIST = True
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
                    print (make_colors(str(n), 'bl') + ". " + self.format_playlist(i, len_x))
                    n = int(n)
                    n += 1
                currentsong = getattr(CLIENT, "currentsong")()
                print("-" * ((cmdw.getWidth() * 2) - 2))
                print(make_colors("current playing:", 'r', 'lw') + " " + self.format_current(currentsong, len_x))
                print("_" * ((cmdw.getWidth() * 2) - 2))
                qp = input(make_colors('Play musics of number or execute commands, [q]uit|e[x]it = quit/exit', 'b', 'ly') + ' ' + make_colors('[number]:', 'b', 'lg') + " ")
                if qp and str(qp).isdigit():
                    if qp.strip().isdigit() and int(qp.strip()) <= len(x):
                        # self.command_execute(["play", str(int(qp.strip()))])
                        en = 0
                        en_max = 10
                        while 1:
                            try:
                                x = getattr(CLIENT, "play")(str(int(qp.strip()) - 1),)
                                break
                            except:
                                if not en == en_max:
                                    en+=1
                                    try:
                                        CLIENT = self.conn(host, port)
                                    except:
                                        pass
                                else:
                                    print(make_colors("ERROR Play track:", 'lw', 'r') + " " + make_colors(qp, 'lw', 'bl'))
                                    time.sleep(1)
                                    print("ERROR:", traceback.format_exc())
                                    break
                        return self.command_execute('playlist')
                    else:
                        return self.command_execute(qp)
                elif qp == 'x' or qp == 'q' or qp == 'exit' or qp == 'quit':
                    sys.exit()
                else:
                    if qp:
                        self.command_execute(qp)
                        return self.command_execute('playlist')
                    else:
                        return self.command_execute('playlist')
            elif 'next' in commands or 'prev' in commands or 'previous' in commands:
                debug(commands = commands)
                if 'prev' in commands:
                    index = commands.index('prev')
                    commands.remove('prev')
                    commands.insert(index, 'previous')
                debug(commands = commands)
                try:
                    x = getattr(CLIENT, commands[0])()
                except:
                    tp, vl, tb = sys.exc_info()
                    mtype = tp.__module__
                    mname = vl.__class__.__name__
                    mesg = str(vl.with_traceback(tb))
                    #print("TYPE:", mtype)
                    #print("NAME:", mname)
                    #print("MESG:", mesg)
                    if "not playing" in str(mesg).lower():
                        print(make_colors("MPD [{}:{}]".format(host, port), 'b', 'lc') + " " + make_colors("IS NOT PLAYING !", 'lw', 'r'))
                    time.sleep(1)
                    self.command_execute("playlist", host, port)
                debug(x = x)
                len_x = 1
                if x:
                    len_x = len(x)
                currentsong = getattr(CLIENT, "currentsong")()
                print("[" + make_colors(commands[0], 'b', 'y') + "] " + make_colors("now is playing:", 'r', 'lw') + " " + self.format_current(currentsong, len_x))
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
                debug(x = x)
                if x:
                    if isinstance(x, dict):
                        for r in x:
                            fg, bg = self.setColor(random.choice(self.BG_COLORS))
                            print(make_colors(str(r).upper() + " " * (15 - len(r)), fg, bg) + make_colors(":", 'y') + " " + make_colors(str(x.get(r)), fg, bg))
                    elif isinstance(x, list):
                        for r in x:
                            if isinstance(r, dict):
                                for a in r:
                                    fg, bg = self.setColor(random.choice(self.BG_COLORS))
                                    print(make_colors(str(a).upper() + " " * (15 - len(a)), fg, bg) + make_colors(":", 'y') + " " + make_colors(str(r.get(a)), fg, bg))
                                print("-" * cmdw.getWidth())
                    else:
                        print(x)
                # print("#"*cmdw.getWidth())    
    
    @classmethod
    def execute(self, host=None, port=None, commands=None):
        host, port = self.ver_host(host, port)
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
                self.ADD = True
                list_command.remove('add')
            debug(ADD = self.ADD)
            debug(list_command=list_command)
            debug(ADD = self.ADD)
            for i in list_command:
                self.command_execute(str(i).strip(), host, port)
        else:
            self.command_execute(q, host, port)

    @classmethod
    def re_execute(self, command, args = (), CLIENT = None, host = None, port = None):
        if not CLIENT:
            CLIENT = self.conn(host, port)
        host, port = self.ver_host(host, port)
        if not args:
            args = ()
        x = None
        while 1:
            try:
                x = getattr(CLIENT, command)(*args)
                break
            except:
                tp, vl, tb = sys.exc_info()
                if vl.__class__.__name__ == 'OSError' and str(vl.with_traceback(tb)) == "cannot read from timed out object":
                    CLIENT = self.conn(host, port)
        return x    
    
    @classmethod
    def usage(self):
        print("\n")
        print("#############################################")
        print("#           MPDc by LICFACE                 #")
        print("#############################################")
        print("\n")
        HOST = self.HOST
        PORT = self.PORT
        usage_txt = """mpdc.py [-h] [-H HOST] [-P PORT] [COMMANDS ...]
    
        positional arguments:
          COMMANDS              Commands, example: find artist coldplay"""
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, usage = usage_txt)
        parser.add_argument('-H', '--host', action='store', help='MPD HOST, default: 127.0.0.1', type=str)
        parser.add_argument('-P', '--port', action='store', help='MPD PORT', type=int)
        #parser.add_argument("COMMANDS", action='store', help="Commands", nargs='*')
        if len(sys.argv) == 1 or sys.argv == ['-h'] or sys.argv == ['--help']:
            parser.print_help()
            print("MPDc by LICFACE")
            print("\n")
            print("MPD_HOST (Environment): ", os.getenv('MPD_HOST'))
            self.execute(None, None, ["playlist"])
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
                PORT = args.port or PORT
                HOST = args.host or HOST
                HOST, PORT = self.ver_host(HOST, PORT)
                os.environ.update({"HOST": str(HOST),})
                os.environ.update({"PORT": str(PORT),})                
                self.execute(HOST, PORT, args.COMMANDS)
            else:
                os.environ.update({"HOST": str(HOST),})
                os.environ.update({"PORT": str(PORT),})                
                self.execute(HOST, PORT, ["playlist"])
    
if __name__ == '__main__':
    print("PID : ", os.getpid())
    # MPDC.generate_pattern("come to me")
    MPDC.usage()
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



