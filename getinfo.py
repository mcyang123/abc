# -*- coding: utf-8 -*-

import requests
import re
import sys
import time
import urllib
import multiprocessing
import math
import writeExcl
reload(sys)
sys.setdefaultencoding('utf8')

time_day = '%Y-%m-%d'
time_time = '%X'
f_c = open(r'target.txt','r')
target_list = {}
for s in f_c:
	ss = s.split(':')
	target_list[ss[1].strip()] = ss[0]
target_id = target_list.keys()
f_c.close()


class getData():
	def __init__(self):
		self.url = 'http://odds.500.com/'#'http://odds.500.com/europe_jczq.shtml'    #get competition info
		self.f_log = open('log.txt','a')
		self.time_now = time.strftime('%Y-%m-%d-%X', time.localtime( time.time()))
		self.f_log.write(self.time_now+":program star.\n")
		print 'log'

	def time_refresh(self):
		self.time_now = time.strftime('%Y-%m-%d-%X', time.localtime( time.time()))

	def get_competition(self):
		'''
		获取指数中心的比赛信息，包括比赛id（fid），比赛队伍（team），场次（scene）、比赛日期（date）
		'''
		competition_list=[]                             #用于返回该函数获取的数据
		re_count = 0                                    #主链接请求次数
		while(re_count<5):                              #若请求失败，重复请求
			try:
				r = requests.get(self.url)
				break
			except :
				error_mes =  "can't open " + self.url+'!\n'
				re_count += 1
		if (re_count>=5):                                #请求5次失败，写入运行日记
			self.time_refresh()
			self.f_log.write(self.time_now+error_mes)
			self.f_log.close()
			raise
		html = r.text
		tbody = re.findall('<tbody id="main-tbody">(.+?)</tbody>',html,re.S)      #解析出tobody代码
		#print 'tbody:' +str(len(tbody))
		if len(tbody)==1:
			tbody = tbody[0]
		else:                                                                     #解析失败，退出程序，记录日志
			error_mes =  "can't get tbody code!\n"
			self.time_refresh()
			self.f_log.write(self.time_now+error_mes)
			self.f_log.close()
			raise
		info_list = re.findall('<tr(.+?)</tr>',tbody,re.S)
		#print 'info:' +str(len(info_list))
		for a,info in enumerate(info_list):
			if a%2 == 0:
				data_c = {}
				#------------------get fid--------------------------------------
				fid = re.findall('data-fid="([0-9]+?)"',info,re.S)
				if len(fid) == 1:
					data_c['fid'] = fid[0]
				else:
					mes =  "can't get fid\n"
					self.time_refresh()
					self.f_log.write(self.time_now+mes)
					data_c['fid'] = ''
				#-----------------get date-------------------------------------
				date = re.findall('<td.+?>([0-9]{2}-[0-9]{2}).+?</td>',info,re.S)
				if len(date)>0:
					data_c['date'] = date[0]
				else:
					mes =  "can't get date\n"
					self.time_refresh()
					self.f_log.write(self.time_now+mes)
					data_c['date'] = ''
				#------------------get team name-------------------------------
				team = re.findall('<a class="team_link".+?>(.+?)</a>',info,re.S)
				if len(team) == 2:
					data_c['team'] = [t.encode('unicode_escape').decode('string_escape') for t in team]
				else:
					mes = "team name error\n"
					self.time_refresh()
					self.f_log.write(self.time_now+mes)
					data_c['team'] = ''
				#-------------------get competition info----------------------
				scene = re.findall('<input.+?'+fid[0]+'.+?>(.+?)</label>',info,re.S)
				if len(scene) == 1:
					data_c['scene'] = scene[0].encode('unicode_escape').decode('string_escape')
				else:
					mes = "scene error\n"
					self.time_refresh()
					self.f_log.write(self.time_now+mes)
					data_c['scene'] = ''
				#----------------------整合数据--------------------------------
				competition_list.append(data_c)
		return competition_list
	
	def get_company(self,fid):
		company_list = []
		html_company = '-1'
		data_raw = ''                          #解析某场比赛原始数据代码
		i = 0
		while html_company!='':
			data_url = 'http://odds.500.com/fenxi1/ouzhi.php?id='+fid+'&ctype=1&start='+str(i*30+1)+'&r=1&style=0&guojia=0&chupan=1'
			re_count = 0
			while(re_count<5):
				try:
					html_company = requests.get(data_url).text.encode('utf8')
					break
				except:
					error_mes =  "can't open " + data.url+'!\n'
					re_count += 1 

			if (re_count>=5):                                #请求5次失败，写入运行日记
				self.time_refresh()
				self.f_log.write(self.time_now+error_mes)
				self.f_log.close()
				raise

			data_raw = data_raw+html_company
			i = i+1
			#break #--------------------------------------------------
		re_str = '<p>(.+?)</p>.+?<p>(.+?)</p>.+?<table(.+?)</table>.+?<table(.+?)</table>.+?<table(.+?)</table>.+?<table(.+?)</table>'
		data_split = re.findall(re_str,data_raw,re.S)         #获取数据行
		for data_temp in data_split:                          #解析每一行数据，获取该行中目标数据
			company_dir = {} 
			cid = re.findall('id="ck(.+?)"',data_temp[0],re.S)  #获取cid
			if len(cid)==1:                                   
				company_dir['cid'] = cid[0]
			else:
				company_dir['cid'] = ''
				mes = "cid error\n"
				self.time_refresh()
				self.f_log.write(self.time_now+mes)

			company_dir['compensation'] = re.findall('<td.+?>(.+?)</td>',data_temp[2],re.S)                         #获取赔率
			company_dir['compensation_change'] = 'class="bg-a"'in data_temp[2] or 'class="bg-b"'in data_temp[2]     #赔率是否变化
			company_dir['kelly'] = re.findall('<td.+?>(.+?)</td>',data_temp[5],re.S)                                #获取凯利
			company_dir['kelly_change'] = 'class="bg-a"'in data_temp[5] or 'class="bg-b"'in data_temp[5]            #凯利是否变化
			company_list.append(company_dir)                                                                        #整合数据
		return company_list
	
	def get_history_kelly(self,fid,cid):
		self.time_refresh()
		t_day = self.time_now[0:10]
		t_time = self.time_now[10:]
		time_d = t_day+'+'+urllib.quote(t_time)
		kelly_url = 'http://odds.500.com/fenxi1/json/ouzhi.php?type=kelly&r=1&fid='+str(fid)+'&cid='+str(cid)+'&time='+time_d
		re_count = 0
		while(re_count<5):                                                           #请求数据
			try:
				html_h_kelly = requests.get(kelly_url).text.encode('utf8')
				break
			except:
				error_mes = "can't open "+kelly_url+'!\n'
				re_count += 1
		if (re_count>=5):                                #请求5次失败，写入运行日记
			self.time_refresh()
			self.f_log.write(self.time_now+error_mes)
			self.f_log.close()
			raise

		h_kellt_data = re.findall('\[(\[.+?\])',html_h_kelly,re.S)                   #解析数据
		if len(h_kellt_data)>0:
			h_kellt_data = h_kellt_data[0]
		else:
			h_kellt_data = ''
		return h_kellt_data

def mulprocess_fun_am(sub_competition,q,abc):
	sub_data = {}
	global target_id
	for c in sub_competition:
		Fid = c['fid']
		company = abc.get_company(Fid)
		for cc in company:
			sub_d = {}
			Cid = cc['cid']
			if Cid in target_id and (not cc['compensation_change']) and (not cc['kelly_change']):   #公司在目标队列中
				h_kelly = abc.get_history_kelly(Fid,Cid)
				flag = True
				for count in range(6):                                                              #数值大于5
					#print cc['compensation'][count][-1]
					if float(cc['compensation'][count]) < 5:
						if cc['compensation'][count][-1] !='0' and cc['compensation'][count][-1] != '5':
							flag = False
							break
				kelly_str = str(cc['kelly'])
				kelly_str.replace("'",'')
				kelly_str.replace(" ",'')
				#print h_kelly
				#print flag
				if flag and (h_kelly =='' or h_kelly[1:15] == kelly_str[1:15]):
					#print 'in'
					sub_d = cc
					sub_d['fid'] = Fid
					sub_d['team'] = c['team']
					sub_d['scene'] = c['scene']
					cid_form = "%04d" % int(cc['cid'])
					Lid = int(c['date'].replace('-','')+c['scene'][-3:]+cid_form)
					sub_data[Lid]=sub_d
		print Fid
	#print 
	q.put(sub_data)

def mulprocess_fun_pm(sub_competition,q,abc):
	sub_data = {}
	global target_id
	time_day = '%Y-%m-%d'
	date = time.strftime(time_day, time.localtime( time.time()))
	file_name = 'data/'+date+'-am.txt'
	try:
		f_d = open(file_name,'r')
		exec(f_d.read())
		f_d.close()
		if data == {}:
			raise

		for c in sub_competition:
			Fid = c['fid']                             #查看比赛id
			data_keys = data.keys()
			for dk in data_keys:                             #循环d
				d = data[dk]
				if Fid == d["fid"]:                    #上午也有该场比赛
					company = abc.get_company(Fid)     #获取该比赛的公司信息
					for cc in company:
						sub_d = {}
						Cid = cc['cid']
						for ddk in data_keys:
							dd = data[ddk]
							if Cid == dd['cid'] and Fid == dd['fid']:   #公司在目标队列中
								sub_d = cc
								sub_d['fid'] = Fid
								sub_d['team'] = c['team']
								sub_d['scene'] = c['scene']
								cid_form = "%04d" % int(cc['cid'])
								Lid = int(c['date'].replace('-','')+c['scene'][-3:]+cid_form)
								sub_data[Lid]=sub_d
								break  #              #处理公司信息
					break	                           #跳出循环d
			print Fid
		q.put_nowait(sub_data)
	except:
		mulprocess_fun_am(sub_competition,q,abc)


def star_spider():   #main

	#-------------------star-------------------------
	data_output = {}

	file_name1 = time.strftime(time_day, time.localtime( time.time()))
	clock = time.strftime(time_time, time.localtime( time.time()))
	#file_name = 'data/'+file_name+'.xls'
	if int(clock[0:2])<12:
		func = mulprocess_fun_am
		file_name = 'data/'+file_name1+'-am.txt'
		Wt = 'w'
	else:
		func = mulprocess_fun_pm
		file_name = 'data/'+file_name1+'-pm.txt'
		Wt = 'a'
	abc = getData()
	competition = abc.get_competition()
	proc_amout = 5  #进程数
	split_num = int(len(competition)/proc_amout)
	q = multiprocessing.Queue()
	p1 = multiprocessing.Process(name = 'spider1',target=func,args=(competition[0:split_num],q,abc))
	p2 = multiprocessing.Process(name = 'spider2',target=func,args=(competition[split_num:2*split_num],q,abc))
	p3 = multiprocessing.Process(name = 'spider3',target=func,args=(competition[2*split_num:3*split_num],q,abc))
	p4 = multiprocessing.Process(name = 'spider4',target=func,args=(competition[3*split_num:4*split_num],q,abc))
	p5 = multiprocessing.Process(name = 'spider5',target=func,args=(competition[4*split_num:],q,abc))

	p1.start()
	p2.start()
	p3.start()
	p4.start()
	p5.start()
	#p1.join()
	#p2.join()
	#p3.join()
	#p4.join()
	#p5.join()
	i = 0
	print '---------------------------'
	while(True):
		z = q.get()
		if not (z == ''):
			data_output = dict(data_output,**z)
			i = i+1
			if i == proc_amout:
				f_txt = open(file_name,'w')
				f_txt.write('data='+str(data_output))
				f_txt.close()
				file_name2 = 'output/'+file_name1+'.xls'
				writeExcl.write_excl(data_output,file_name2,Wt)
				abc.f_log.close()
				break


if __name__ == '__main__':
	
	multiprocessing.freeze_support()
	now_time= time.strftime('%X', time.localtime( time.time()))
	if now_time<'12:00:00':
		Tflag = 'am'
	else:
		Tflag = 'pm'
	print u'爬虫已启动....'
	while (True):
		now_time= time.strftime('%X', time.localtime( time.time()))
		if Tflag == 'am' and (now_time>'10:00:00' and now_time < '10:20:00'):
			print 'spider...'
			Tflag = 'pm'
			star_spider()
			print 'end'
		if Tflag == 'pm' and (now_time>'16:30:00' and now_time < '16:50:00'):
			print 'spider...'
			Tflag = 'am'
			star_spider()
			
			print 'end'
		else:
			pass
			#print now_time
	'''
	abc = getData()
	com = abc.get_competition()
	print com
	'''
