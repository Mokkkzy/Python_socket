from multiprocessing.connection import wait
import socket
from sqlite3 import connect
import sys
import threading
import time

streams = [None, None]
debug = 1


def _usage():
    print('Usage: ./innerServer_connect.py stream1 stream2\nstream: l:port or c:host:port')


def _get_another_stream(num):

    if num == 0:
        num = 1
    elif num == 1:
        num = 0
    else:
        raise 'ERROR'

    while True:
        if streams[num] == 'quit':
            print('can not connect to the target, quit')
            sys.exit(1)

        if streams[num] is not None:
            return streams[num]
        elif streams[num] is None and streams[num ^ 1] is None:
            print('stream CLOSED')
            return None
        else:
            time.sleep(1)


def _xstream(num, s1, s2):
    try:
        while True:
            buff = s1.recv(1024)
            if debug > 0:
                print('%d recv' % num)
            if len(buff) == 0:
                print('%d one closed' % num)
                break
            s2.sendall(buff)
            if debug > 0:
                print('%d sendall' % num)
    except:
        print('%d connect closed.' % num)
        
    try:
        s1.shutdown(socket.SHUT_RDWR) #shutdown直接破坏socket连接
        # RD（不能再读）0  WR（不能再写）1 RDWR（读写都不能）2 关闭方式的参数
        s1.close()
    except:
        pass
    
    try:
        s2.shutdown(socket.SHUT_RDWR)
        s2.close()
    except:
        pass
    
    streams[0] = None
    streams[1] = None
    print('%d CLOSED' % num)
# _server用于收    
def _server(port,num):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0',port))
    srv.listen(1)
    while True:
        conn, addr = srv.accept()
        print('connected from: %s' % str(addr))
        streams[num] = conn
        s2 = _get_another_stream(num)
        _xstream(num,conn,s2)
# _connect用于发，跟_server原理上差不多        
def _connect(host,port,num):
    not_connect_time = 0
    wait_time = 36
    try_cnt = 199
    while True:
        if not_connect_time>try_cnt:
            streams[num] = 'quit'
            print('not connected')
            return None
        
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conn.connect((host,port))
        except Exception:
            print('can not connect %s:%s' % (host,port))
            not_connect_time += 1
            time.sleep(wait_time)
            continue
        
        print('connected to %s:%i' % (host,port))
        streams[num] = conn
        s2 = _get_another_stream(num)
        _xstream(num, conn, s2)
        
def main():
    if len(sys.argv) != 3:
        _usage()
        sys.exit(1)
    tlist = [] #threading list
    targv = [sys.argv[1],sys.argv[2]]
    for i in [0,1]:
        s = targv[i] #stream 描述 c:ip:port / l:port
        s1 = s.split(':')
        if len(s1) == 2 and (s1[0] == 'l' or s1[0] == 'L'):
            t = threading.Thread(target=_server, args=(int(s1[1],i)))
            tlist.append(t)
        elif len(s1) == 3 and (s1[0] == 'c' or s1[0] =='C'):
            t = threading.Thread(target=_connect,args=(int(s1[1]),int(s1[2]),i))
            tlist.append(t)
        else:
            _usage()
            sys.exit(1)
    
    for t in tlist:
        t.start()
    for t in tlist:
        t.join()
    sys.exit(0)
    
if __name__ =='__main__':
    main()
    
        
