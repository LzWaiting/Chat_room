#!/usr/bin/env python3
#coding=utf-8

'''
name:  Laz
email:  Laz@
data:  2019-3
introduce:  File_load Server(ftp文件服务器)
env:  python3.5
module:  第三方模块
'''

# 模块调用
from socket import *
import os
import sys
import time
import signal

# 文件库路径
FILE_PATH = "/home/tarena/python/PythonProcess/code/ftp/ftpfile/"

# 创建套接字
HOST = ""
PORT = 8888
ADDR = (HOST,PORT)

# 将文件服务器功能写入类中
class FtpServer(object):
	def __init__(self,connfd):
		self.connfd = connfd

	def read_file(self):
		# 获取文件库文件内容
		file_list = os.listdir(FILE_PATH)
		# 判断文件库内容是否满足请求
		if not file_list:
			self.connfd.send("文件库为空".encode())
			return
		else:
			self.connfd.send(b"OK")
			time.sleep(0.1)	
		# 发送文件列表
		files = ''
		for file in file_list:
			if file[0] != '.' and os.path.isfile(FILE_PATH+file):
				files += (file + '#')
		self.connfd.send(files.encode())

	def load_file(self,filename):
		try:
			f = open(FILE_PATH+filename,'rb')
		except:
			self.connfd.send(('要下载的%s文件不存在'%filename).encode())
			return
		self.connfd.send(b'OK')
		time.sleep(0.1)
		while True:
			data = f.read(4096)
			if not data:
				time.sleep(0.1)
				self.connfd.send(b'##')
				break
			self.connfd.send(data)
		f.close()
		print('%s文件发送完毕'%filename)

	def upload_file(self,filename):
		try: 
			f = open(FILE_PATH+filename,'wb')
		except:
			self.connfd.send(('%s上传失败'%filename).encode())
			return
		self.connfd.send(b'OK')
		while True:
			data = self.connfd.recv(4096)
			if data == b'##':
				break
			f.write(data)
		f.close()
		print('%s文件上传完毕'%filename)


def main():
	sockfd = socket()
	sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	sockfd.bind(ADDR)
	sockfd.listen(5)

	# 处理子进程退出
	signal.signal(signal.SIGCHLD,signal.SIG_IGN)
	print("Listen the port 8888...")

	while True:
		try:
			connfd,addr = sockfd.accept()
		except KeyboardInterrupt:
			sockfd.close()
			sys.exit("服务器退出")
		except Exception as e:
			print("服务器异常:",e)
			continue
		print('已连接客户端:',addr)
		# 创建子进程
		pid = os.fork()
		if pid == 0:
			sockfd.close()
			ftp = FtpServer(connfd)
			# 判断客户端请求
			while True:
				data = connfd.recv(1024).decode()
				if not data or data[0] == 'Q':
					connfd.close()
					sys.exit('客户端退出')
				elif data[0] == 'R':
					ftp.read_file()
				elif data[0] == 'L':
					filename = data.split(' ')[-1]
					ftp.load_file(filename)
				elif data[0] == 'U':
					filename = data.split(' ')[-1]
					ftp.upload_file(filename)
		else:
			connfd.close()
			continue
	
if __name__ == "__main__":
	main()