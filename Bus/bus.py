'''司机和售票员的故事
	* 创建父子进程分别代表司机和售票员
	* 当售票员收到SIGINT信号,给司机发送SIGUSR1信号,此时司机打印'老司机开车了'
	* 当售票员收到SIGQUIT信号,给司机发送SIGUSR2信号,此时司机打印'车速有点快,系好安全带'
	* 当司机捕捉到SIGTSTP信号,给售货员发送SIGUSR1,售票员打印'到站了,请下车'
	* 到站后 售票员先下车,司机再下车(子进程先退出)
	说明:SIGINT SIGQUIT SIGTSTP 从键盘发出
'''
from multiprocessing import Process
from signal import *
import os,sys

def handler(sig,frame):
	if sig == SIGINT:
		os.kill(os.getppid(),SIGUSR1)
	elif sig == SIGQUIT:
		os.kill(os.getppid(),SIGUSR2)
	elif sig == SIGUSR1:
		pass
		if pid == 0:
			sys.exit("到站了,请下车")
		else:
			print('老司机开车了')
	elif sig == SIGUSR2:
		print('车速有点快,系好安全带')
	elif sig == SIGTSTP:
		os.kill(pid,SIGUSR1)

def conductor():
	signal(SIGINT,handler)
	signal(SIGQUIT,handler)
	signal(SIGUSR1,handler)
	signal(SIGTSTP,SIG_IGN)
	while True:
		pass

def driver():
	signal(SIGUSR1,handler)
	signal(SIGUSR2,handler)
	signal(SIGTSTP,handler)
	signal(SIGINT,SIG_IGN)
	signal(SIGQUIT,SIG_IGN)
	os.wait()

pid = os.fork()

if pid < 0:
	print('failed')
elif pid == 0:
	conductor()
else:
	driver()

