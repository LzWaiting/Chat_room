#!/usr/bin/env python3
#coding=utf-8

'''
name:  Levi
email:  lvze@tedu.cn
data:  2019-3
introduce:  Chatroom client
env:  python3.5
module:  第三方模块
'''

# 调用模块
from socket import *
import os,sys

# 发送消息
def send_msg(s,name,addr):
	while True:
		text = input(">>")
		# 如果输入quit表示退出
		if text.strip() == 'quit':
			msg = 'Q '+name
			s.sendto(msg.encode(),addr)
			sys.exit('退出聊天室')
		msg = 'C %s %s'%(name,text)
		s.sendto(msg.encode(),addr)

# 接收消息
def recv_msg(s):
	while True:
		data,addr = s.recvfrom(2048)
		if data.decode() == 'EXIT':
			sys.exit(0)
		print(data.decode()+'\n>>',end='')

# 实现创建套接字,登录,创建子进程
def main():
	# 从命令行获取服务端地址
	if len(sys.argv) < 3:
		print('argv is error')
		return
	HOST = sys.argv[1]
	POST = int(sys.argv[2])
	ADDR = (HOST,POST)
	# 创建套接字
	s = socket(AF_INET,SOCK_DGRAM)
	s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	while True:
	    name = input('请输入姓名:')
	    # 创建请求类型
	    msg = 'L '+name
	    # 发送登录请求
	    s.sendto(msg.encode(),ADDR)
	    # 等待服务器回复
	    data,ADDR = s.recvfrom(1024)
	    if data.decode()=='OK':
	    	print('您已进入聊天室')
	    	break
	    else:
	    	# 不成功服务器回复不允许原因
	    	print(data.decode())
	# 创建父子进程
	pid = os.fork()
	if pid < 0:
		sys.exit('创建子进程失败')
	elif pid == 0:
		send_msg(s,name,ADDR)
	else:
		recv_msg(s)

if __name__ == '__main__':
	main()