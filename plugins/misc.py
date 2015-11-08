import socket
import subprocess
import time

from util import hook, http

socket.setdefaulttimeout(10)  # global setting


def get_version():
    try:
        stdout = subprocess.check_output(['git', 'log', '--format=%h'])
    except:
        revnumber = 0
        shorthash = '????'
    else:
        revs = stdout.splitlines()
        revnumber = len(revs)
        shorthash = revs[0]

    http.ua_skybot = 'Skybot/r%d %s (http://github.com/rmmh/skybot)' \
        % (revnumber, shorthash)

    return shorthash, revnumber


# autorejoin channels
@hook.event('KICK')
def rejoin(paraml, conn=None):
    if paraml[1] == conn.nick:
        if paraml[0].lower() in conn.conf.get("channels", []):
            conn.join(paraml[0])


@hook.event('004')
def onjoin(paraml, conn=None):
    # identify to services
    nickserv_password = conn.conf.get('nickserv_password', '')
    nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
    nickserv_command = conn.conf.get('nickserv_command', 'IDENTIFY %s')
    if nickserv_password:
        conn.msg(nickserv_name, nickserv_command % nickserv_password)
        time.sleep(1)

    # set mode on self
    mode = conn.conf.get('mode')
    if mode:
        conn.cmd('MODE', [conn.nick, mode])

    # join channels
    for channel in conn.conf.get("channels", []):
        conn.join(channel)
        time.sleep(1)  # don't flood JOINs

    # set user-agent
    ident, rev = get_version()


@hook.regex(r'^\x01VERSION\x01$')
def version(inp, notice=None):
    ident, rev = get_version()
    notice('\x01VERSION h %s - https://git.xeserv.us/xena/h'
           '\x01' % ident)
