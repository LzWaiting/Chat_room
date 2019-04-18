#!/usr/bin/env python3
#coding=utf-8

'''
name: Laz
email: 	
data: 2019-3
introduce: File_load Client
env: python3.5
module: 第三方模块
'''

# 调用模块
from socket import *
import os
import sys
import time

# 菜单选项
def menu():
	print('+---+------------------------------+')
	print('| 1 |查看服务端文件                +')
	print('+---+------------------------------+')
	print('| 2 |下载文件到本地                +')
	print('+---+------------------------------+')
	print('| 3 |上传文件到服务端              +')
	print('+---+------------------------------+')
	print('| 4 |退出                          +')
	print('+---+------------------------------+')

# 客户端
class FtpClient(object):
	def __init__(self,sockfd):
		self.sockfd = sockfd

	def read_file(self):
		self.sockfd.send(b'R')	# 发送请求
		data = self.sockfd.recv(1024).decode()
		if data == 'OK':
			data = self.sockfd.recv(4096).decode()
			files = data.split('#')
			for file in files:
				print(file)
			print('文件列表展示完毕\n')
		else:
			# 打印失败原因
			print(data)

	def load_file(self,filename,file_path):
		self.sockfd.send(('L %s'%filename).encode())
		data = self.sockfd.recv(1024).decode()
		if data == 'OK':
			try:	
				f = open(file_path+filename,'wb')
				while True:
					msg = self.sockfd.recv(4096)
					if msg == b'##':
						break
					f.write(msg)
				f.close()
				print('%s文件下载完毕'%filename)
			except Exception as e:
				print('Error:',e)
		else:
			print(data)

	def upload_file(self,filename,file_path):
		try:
			f = open(file_path+filename,'rb')
		except:
			print('要上传的文件%s不存在'%filename)
			return
		self.sockfd.send(('U %s'%filename).encode())
		data = self.sockfd.recv(1024).decode()
		if data == 'OK':
			while True:
				msg = f.read(4096)
				if not msg:
					time.sleep(0.1)
					self.sockfd.send(b'##')
					break
				self.sockfd.send(msg)
			f.close()
			print('%s文件上传完毕'%filename)
		else:
			print(data)

	def server_exit(self):
		self.sockfd.send(b'Q')


# 网络连接
def main():
	if len(sys.argv) < 3:
		print('argv is error')
		return
	# 创建套接字
	HOST = sys.argv[1]
	PORT = int(sys.argv[2])
	ADDR = (HOST,PORT)	# 文件服务端地址 
	
	sockfd = socket()
	sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	try:
		sockfd.connect(ADDR)
	except:
		print('连接服务器失败')
		return
	
	ftp = FtpClient(sockfd)	# 生成功能类对象
	while True:	
		menu()
		try:
			opt = input(">>选项:")
			if opt[0] == "1":
				ftp.read_file()		# 返回文件名称列表信息
			elif opt[0] == "2":
				filename = opt.split(' ')[1]
				file_path = opt.split(' ')[-1]
				ftp.load_file(filename,file_path)
			elif opt[0] == "3":
				filename = opt.split(' ')[1]
				file_path = opt.split(' ')[-1]
				ftp.upload_file(filename,file_path)
			elif opt[0] == "4":
				ftp.server_exit()
				sockfd.close()
				sys.exit('谢谢使用')
			else:
				raise ValueError
		except ValueError:
			print('输入有误,请输入正确命令')
			continue
		except KeyboardInterrupt:
			sockfd.close()
			sys.exit('谢谢使用')
		except Exception as e:
			print("Error:",e)


if __name__ == "__main__":
	main()