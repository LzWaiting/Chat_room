#!/usr/bin/env python3
#coding=utf-8

'''
name: Laz
email: xxx 
data: 2019-4
introduce: Dict Client
module: pymysql
env: xxx
'''

from socket import *
import getpass
import sys

def main():
	if len(sys.argv) < 3:
		print('argv is error')
		return
	HOST = sys.argv[1]
	PORT = int(sys.argv[2])
	ADDR = (HOST,PORT)
	# 创建网络连接
	s = socket(AF_INET,SOCK_STREAM)
	s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	try:
		s.connect(ADDR)
	except Exception as e:
		print(e)
		return
	while True:
		# 进入一级界面
		print('''
			============ Welcome ============
			| 1.Register | 2.Login | 3.Exit |
			=================================
			''')
		
		try:
			cmd = int(input('输入选项>>'))
		except KeyboardInterrupt:
			s.send(b'Q')
			s.close()
			sys.exit('谢谢使用')
		except Exception as e:
			print('命令错误',e)
			continue
		
		if cmd not in [1,2,3]:
			print('请输入正确选项')
			sys.stdin.flush()	# 清除标准输入
			continue
		
		elif cmd == 1:
			do_register(s)

		elif cmd == 2:
			name = do_login(s)
			if name:	
				login(s,name)
			else:
				print('登录失败')

		elif cmd == 3:
			s.send(b'E')
			s.close()
			sys.exit('谢谢使用')


def do_register(s):
	while True:	
		name = input('User:')
		password = getpass.getpass()
		password1 = getpass.getpass('Again:')
		# 判断输入信息正确性
		if (' 'in name) or (' 'in password):
			print('用户名和密码不允许有空格')
			continue
		if password != password1:
			print('两次密码不一致')
			continue
		# 输入信息正确,发送服务端注册
		msg = 'R {} {}'.format(name,password)
		s.send(msg.encode())
		# 等待回复			
		data = s.recv(128).decode()
		if data == 'OK':
			print('注册成功')
			login(s,name)
		elif data == 'EXISTS':
			print('用户已存在')
		else:
			print('注册失败')
		return
	
def do_login(s):
	while True:
		name = input('User:')
		password = getpass.getpass()
		msg = 'L {} {}'.format(name,password)
		s.send(msg.encode())
		data = s.recv(128).decode()
		if data == 'OK':
			print('登录成功')
			return name
		elif data == 'UN':
			print('您输入的User不存在')
			return None
		elif data == 'UP':
			print('您输入的password不正确')
			return None

# 进入二级界面
def login(s,name):
	while True:
		print('''
			============查询界面============
			| 1.Query | 2.History | 3.Exit |
			================================
			''')
		try:
			cmd = int(input('输入选项>>'))
		except Exception as e:
			print('命令错误',e)
			continue
		if cmd not in [1,2,3]:
			print('请输入正确选项')
			sys.stdin.flush()
			continue
		elif cmd == 1:
			do_query(s,name)
		elif cmd == 2:
			do_history(s,name)
		elif cmd == 3:
			return

def do_query(s,name):
	while True:
		word = input('输入要查询的单词>>')
		if word == '##':
			break
		msg = 'Q {} {}'.format(name,word)
		s.send(msg.encode())
		data = s.recv(128).decode()
		if data == 'OK':
			data = s.recv(1024).decode()
			print(data)
		else:
			print('没有查到该单词')


def do_history(s,name):
	msg = 'H {}'.format(name)
	s.send(msg.encode())
	data = s.recv(128).decode()
	if data == 'OK':
		while True:
			data = s.recv(1024).decode()
			if data == '##':
				break
			print(data)
	else:
		print('没有历史查询记录')

if __name__ == '__main__':
	main()