#!/usr/bin/env python
#coding:utf8
import sys,os,re
import subprocess
import optparse
import pexpect
reload(sys)
sys.setdefaultencoding('utf-8')


class check_mysql_mongo_process:
	def __init__(self,node_name):
		self.node_name = node_name
		self.server_dir = "/data/%s/server"% self.node_name
		self.server_process_count = os.popen("ps aux|grep %s/server|grep -v grep|wc -l"%(self.server_dir)).read().strip()
		self.mongo_process_count = os.popen("ps aux|grep %s|grep mongo|grep -v grep|wc -l"%(self.node_name)).read().strip()
		self.mysql_process_count = os.popen("ps aux|grep mysql|grep -v grep|wc -l").read().strip()
		self.mongo_dir = "/data/master_mongodb/%s"% self.node_name
		self.mysql_dir = "/data/mysql/3306/"
		self.pwd = os.popen("cat /root/.pw").read().strip()
		if not os.path.exists("%s"% self.server_dir):
			print '\033[1;31;40m[%s]不存在此游戏服\033[0m'% self.node_name
			sys.exit(1)
		if int(self.server_process_count) > 3:
			print '\033[1;31;40m[%s]游戏进程已经开启\033[0m'% self.node_name
			sys.exit(2)
		else:
			if os.path.exists("%s/daemon.pid"% self.server_dir):
				os.remove("%s/daemon.pid")% self.server_dir
	def start_mongo_process(self):
		if int(self.mongo_process_count) - 1  == 0:
			if os.path.exists("%s/daemon.pid"% self.mongo_dir):
				os.remove("%s/pid_mongod.pid")% self.mongo_dir
			res_mongo = subprocess.call("sh %s/mongodb_start_master.sh"% self.mongo_dir,shell=True)
			if int(res_mongo) == 0:
				print '\033[1;32;40m[%s]mongo开启成功\033[0m'% self.node_name
			else:
				print '\033[1;31;40m[%s]mongo开启失败\033[0m'% self.node_name
				sys.exit(2)
		else:
			print '\033[1;32;40m[%s]mongo进程已经开启\033[0m'% self.node_name
	def start_mysql_process(self):
		if int(self.mysql_process_count) - 1 == 0:
			if os.path.exists("%s/daemon.pid"% self.mysql_dir):
				os.remove("%s/mysql-3306.pid")% self.mysql_dir
			res_mysql = subprocess.call("sh %s/start_mysql.sh"% self.mysql_dir,shell=True)
			if int(res_mysql) == 0:
				print '\033[1;32;40m[%s]mysql开启成功\033[0m'% self.node_name
			else:
				print '\033[1;31;40m[%s]mysql开启失败\033[0m'% self.node_name
				sys.exit(2)
		else:
			print '\033[1;32;40m[%s]mysql进程已经开启\033[0m'% self.node_name
	def stop_mongo_process(self):
		if int(self.mongo_process_count) - 1  == 0:
			print '\033[1;32;40m[%s]mongo进程已经关闭\033[0m'% self.node_name
		else:
			if os.path.exists("%s/daemon.pid"% self.mongo_dir):
				os.remove("%s/pid_mongod.pid")% self.mongo_dir
			res_mongo = subprocess.call("sh %s/close_mongodb_master_by_pidfile.sh"% self.mongo_dir,shell=True)
			if int(res_mongo) == 0:
				print '\033[1;32;40m[%s]mongo关闭成功\033[0m'% self.node_name
			else:
				print '\033[1;31;40m[%s]mongo关闭失败\033[0m'% self.node_name
				sys.exit(3)
	def stop_mysql_process(self,mypassword):
		if int(self.mysql_process_count) - 1 == 0:
			print '\033[1;32;40m[%s]mysql进程已经关闭\033[0m'% self.node_name
		else:
			if os.path.exists("%s/daemon.pid"% self.mysql_dir):
				os.remove("%s/mysql-3306.pid")% self.mysql_dir
			try:
				res_mysql = pexpect.spawn("sh %s/close_mysql.sh"% self.mysql_dir)
				res_mysql.expect('Enter password:')
				res_mysql.sendline(mypassword)
				#time.sleep(10)
				res_mysql.interact()
				print '\033[1;32;40m[%s]mysql关闭成功\033[0m'% self.node_name
			except pexpect.EOF:
				res_mysql.close()
				print '\033[1;31;40m[%s]mysql关闭失败\033[0m'% self.node_name


if __name__ == "__main__":
	active_list = ['start','stop']
	db_name_list = ['mysql','mongo']
	usage = '''./%prog -n node_name -a start|stop -d mysql|mongo
    '''
	parser = optparse.OptionParser(
        usage   = usage,
    )
	parser.add_option(
					"-n", "--node_name",
					dest="node_name",  
					help="服名NODE_NAME")
	parser.add_option(
					"-a", "--action",
					dest="active",
					choices=active_list,
					type="choice",
					help="停止or启动对应服mongo或mysql进程") 
	parser.add_option(
					"-d", "--db_name",
					dest="db_name",
					choices=db_name_list,
					type="choice",
					help="mongo or mysql") 
	(options, args) = parser.parse_args()
	err_msg = '参数不对，请输--help查看详细说明！'	
	if options.node_name and options.active and options.db_name:
		check = check_mysql_mongo_process(options.node_name)
		if options.active == "start":
			if options.db_name == "mysql":
				check.start_mysql_process()
			elif options.db_name == "mongo":
				check.start_mongo_process()	
		elif options.active == "stop":
			if options.db_name == "mysql":
				password = check.pwd
				check.stop_mysql_process(password)
			elif options.db_name == "mongo":
				check.stop_mongo_process()	
		else:
			parser.error(err_msg)
	else:
		parser.error(err_msg)
