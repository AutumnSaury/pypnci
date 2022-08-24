import ctypes
import inspect
import socket
import sys
from threading import Thread
from xmlrpc.client import boolean

class TCPConnection:
  client = None
  def __init__(self, is_server: boolean, port: int, dest: str=None):
    self.sock = socket.socket()
    # try:
    if is_server:
      self.setup_server(port)
    else:
      self.setup_client(dest, port)

  def setup_server(self, port: int):
    self.sock.bind(('0.0.0.0', port))
    self.sock.listen(1)
    self.client, client_addr = self.sock.accept()
    self.in_thread = Thread(target=self.__send_msg, args=(self.client, ))
    self.out_thread = Thread(target=self.__recv_msg, args=(self.client, ))
    self.in_thread.start()
    self.out_thread.start()
    print('A client(' + client_addr[0] + ') has established connection', file=sys.stderr)

  def setup_client(self, addr: str, port: int):
    try:
      self.sock.connect((addr, port))
    except ConnectionRefusedError:
      print('Connection refused')
      self.sock.close()
      exit(1)
    self.in_thread = Thread(target=self.__send_msg, args=(self.sock, ))
    self.in_thread.start()
    self.out_thread = Thread(target=self.__recv_msg, args=(self.sock, ))
    self.out_thread.start()
    print('Connection established', file=sys.stderr)

  def __send_msg(self, s: socket.socket):
    while True:
      line = sys.stdin.buffer.readline()
      if line == b'':
        self.clean()
      s.send(line)

  def __recv_msg(self, s: socket.socket):
    while True:
      line = s.recv(1024)
      sys.stdout.buffer.write(line)
      sys.stdout.flush()

  # Do some clean up
  def close(self, _=None, __=None):
    self.sock.close()
    if self.client:
      self.client.close()
    if self.in_thread.is_alive():
      stop_thread(self.in_thread)
    if self.out_thread.is_alive():
      stop_thread(self.out_thread)

def stop_thread(thread):
  _async_raise(thread.ident, SystemExit)

def _async_raise(tid, exctype):
  """raises the exception, performs cleanup if needed"""
  tid = ctypes.c_long(tid)
  if not inspect.isclass(exctype):
      exctype = type(exctype)
  res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
  if res == 0:
      raise ValueError("invalid thread id")
  elif res != 1:
      # """if it returns a number greater than one, you're in trouble,
      # and you should call it again with exc=NULL to revert the effect"""
      ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
      raise SystemError("PyThreadState_SetAsyncExc failed")