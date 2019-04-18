#!/usr/bin/env python3
#coding=utf-8

'''
name: Laz
email: xxx 
data: 2019-4
introduce: Dict Server
module: pymysql
env: xxx
'''

from socket import *
from pymysql import *
import os
import re
import sys
import time
import signal

# 定义需要的全局变量
DICT_TEXT = './dict.txt'
HOST = '0.0.0.0'
PORT = 8000
ADDR = (HOST,PORT)

def main():
	# 创建数据库连接
	db = connect('localhost','root','123456','dict')
	# 创建套接字
	s = socket(AF_INET,SOCK_STREAM)
	s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	s.bind(ADDR)
	s.listen(5)
	# 忽略子进程信号
	signal.signal(signal.SIGCHLD,signal.SIG_IGN)
	while True:
		try:
			c,addr = s.accept()
			print('Connect from',addr)
		except KeyboardInterrupt:
			s.close()
			sys.exit('服务器退出')
		except Exception as e:
			print(e)
			continue
		# 创建子进程
		pid = os.fork()
		if pid == 0:
			s.close()
			do_child(c,db)
		else:
			c.close()
			continue

def do_child(c,db):
	# 循环接收客户端请求
	while True:
		data = c.recv(128).decode()
		print(c.getpeername(),':',data)
		
		if (not data) or data[0] == 'E':
			c.close()
			sys.exit(0)
		elif data[0] == 'R':
			do_register(c,db,data)
		elif data[0] == 'L':
			do_login(c,db,data)
		elif data[0] == 'Q':
			do_query(c,db,data)
		elif data[0] == 'H':
			do_history(c,db,data)

def do_login(c,db,data):
	print('登录操作')
	l = data.split(' ')
	name = l[1]
	password = l[2]
	cursor = db.cursor()
	sql = "select * from user where name='%s'"%name
	cursor.execute(sql)
	r = cursor.fetchone()
	if r != None:
		if r[2] == password:
			print('%s登录成功'%name)
			c.send(b'OK')
		else:
			c.send(b'UP')
		return
	else:
		c.send(b'UN')
		return

def do_register(c,db,data):
	print('注册操作')
	l = data.split(' ')
	name = l[1]
	password = l[2]
	# 创建游标对象
	cursor = db.cursor()
	# 确认用户是否存在
	sql = "select * from user where name = '%s'"%name
	cursor.execute(sql)
	r = cursor.fetchone()
	# 存在，返回’EXISTS‘
	if r != None:
		c.send(b'EXISTS')
		return
	# 不存在，将注册信息插入到数据库	
	sql = "insert into user (name,password) values \
	('%s','%s')"%(name,password)
	try:
		cursor.execute(sql)
		db.commit()
		c.send(b'OK')
	except:
		db.rollback()
		c.send(b'FALL')
	else:
		print('%s注册成功' % name)
	return

def do_query(c,db,data):
	print('查询操作')
	l = data.split(' ')
	name = l[1]
	word = l[2]
	cursor = db.cursor()
	
	def insert_history():
		tm = time.ctime()
		sql = "insert into hist (name,word,time) values \
		('%s','%s','%s')"%(name,word,tm)
		try:
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()

	# 文本查询
	try:
		f = open(DICT_TEXT)
	except:
		c.send(b'FALL')
		return

	for line in f:
		tmp = line.split(' ')[0]
		if tmp > word:
			c.send(b'FALL')
			f.close()
			return
		elif tmp == word:
			c.send(b'OK')
			time.sleep(0.1)
			c.send(line.encode())
			f.close()
			insert_history()
			return
	c.send(b'FALL')
	f.close()


def do_history(c,db,data):
	print('查阅历史记录操作')
	l = data.split(' ')
	name = l[1]
	cursor = db.cursor()
	sql = "select * from hist where name = '%s'"%name
	cursor.execute(sql)
	r = cursor.fetchmany(10)
	if not r:
		c.send(b'FALL')
		return
	else:
		c.send(b'OK')
	for line in r:
		time.sleep(0.1)
		msg = "%s    %s    %s"%(line[1],line[2],line[3])
		c.send(msg.encode())
	time.sleep(0.1)
	c.send(b'##')

if __name__ == '__main__':
	main()