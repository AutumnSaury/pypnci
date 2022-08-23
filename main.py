from tcp_connection import TCPConnection
import click, signal

@click.command()
@click.option('-l', is_flag=True, default=False, help='Server mode')
@click.argument('dest', required=False, type=str)
@click.argument('port', required=False, type=int)

def cli(port: int, l: bool=False, dest: str=None):
  if dest and not port:
    try:
      port = int(dest)
    except:
      pass
  if not dest and not port:
    cli(['--help'])
  try:
    session = TCPConnection(l, port, dest)
    signal.signal(2, session.close)
  except PermissionError:
    print('Permission denied')
    exit(1)
  finally:
    if 'session' in locals().keys():
      session.in_thread.join()
      session.close()
    exit(0)

if __name__ == '__main__':
  cli()