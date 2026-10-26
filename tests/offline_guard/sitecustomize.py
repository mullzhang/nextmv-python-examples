"""検証で起動する Python 子プロセスのネットワーク接続を拒否する。"""

import socket


def deny_network(*args, **kwargs):
    raise RuntimeError("検証中のネットワーク接続は禁止されています")


socket.socket.connect = deny_network
socket.socket.connect_ex = deny_network
socket.create_connection = deny_network
