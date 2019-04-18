from pymysql import *
import re


# 创建mysql数据库表1
db = connect(host='localhost',user='root',password='123456',database='dict',charset='utf8')

# 2. 利用db方法创建游标对象
cur = db.cursor()

with open('./dict.txt') as f:
# 3. 利用游标对象的execute()方法执行SQL命令
	for line in f:
		l = re.split(r'\s+',line)
		word = l[0]
		interpret = ' '.join(l[1:])
		sql = "insert into words (word,interpret) values\
			('%s','%s');" % (word,interpret)
		try:
			cur.execute(sql)
			# 4. 提交到数据库执行
			db.commit()
		except:
			db.rollback()

# 5. 关闭游标对象
cur.close()

# 6. 断开数据库连接
db.close()