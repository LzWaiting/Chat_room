#!/usr/bin/env python3
#coding=utf-8

'''
name:  Levi
email:  lvze@tedu.cn
data:  2019-3
introduce:  Chatroom server
env:  python3.5
module:  第三方模块
'''

# 搭建网络连接
from socket import *
import os,sys

# 4. 登录判断
def do_login(s,user,name,addr):
	if (name in user) or name == '管理员':
		s.sendto("\n该用户已存在".encode(),addr)
		return
	s.sendto(b'OK',addr)
	# 通知其他人
	msg = ("\n欢迎%s进入聊天室"%name).encode()
	for n in user:
		s.sendto(msg,user[n])
	# 插入用户信息
	user[name] = addr

# 5. 聊天信息接收
def do_chat(s,user,name,text):
	msg = ("\n%s说:%s"%(name,text)).encode()
	for n in user:
		if n != name:
			s.sendto(msg,user[n])

# 用户退出
def do_quit(s,user,name):
	msg = ('\n%s退出了聊天室'%name).encode()
	for n in user:
		if n == name:
			s.sendto(b'EXIT',user[n])
		else:
			s.sendto(msg,user[n])
	# 删除用户信息
	del user[name]


# 2. 父进程函数,接收客户端请求
def do_parent(s):
	# 存储结构{'张三':("127.0.0.1",8888)}
    user = {}
	# 接收客户端请求
    while True:
	    msg,addr = s.recvfrom(1024)
	    # 判断请求类型
	    msgList = msg.decode().split(' ')
	    # 区分请求类型
	    if msgList[0] == 'L':
	    	do_login(s,user,msgList[1],addr)
	    elif msgList[0] == 'C':
	    	do_chat(s,user,msgList[1]," ".join(msgList[2:]))
	    elif msgList[0] == 'Q':
	    	do_quit(s,user,msgList[1])

# 3. 子进程函数,做管理员喊话
def do_child(s,addr):
	while True:
		data = input('管理员消息:')
		msg = ('C 管理员 %s'%data).encode()
		s.sendto(msg,addr)

# 1. 创建网络,创建进程,调用功能函数
def main():
    # server address
    ADDR = ('0.0.0.0',8888)

    # 创建套接字
    s = socket(AF_INET,SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)

    # 创建一个单独的进程处理管理员喊话功能
    pid = os.fork()
    if pid < 0:
    	sys.exit('创建进程失败')
    elif pid == 0:
    	do_child(s,ADDR)
    else:
    	do_parent(s)
				

if __name__ == '__main__':
	main()