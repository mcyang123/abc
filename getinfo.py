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

	def get_competition(self):
		competition_list=[]
		try:
			r = requests.get(self.url)
		except :
			print "can't open http://odds.500.com/europe_jczq.shtml"
			raise urlOpenError
		html = r.text
		tbody = re.findall('<tbody id="main-tbody">(.+?)</tbody>',html,re.S)
		if len(tbody)==1:
			tbody = tbody[0]
		else:
			print "can't get tbody code"
			raise
		info_list = re.findall('<tr (data-fid="[0-9]+?" data.+?>.+?)</tr>',tbody,re.S)
		for info in info_list:
			data_c = {}
			#------------------get fid--------------------------------------
			fid = re.findall('data-fid="([0-9]+?)"',info,re.S)
			if len(fid) == 1:
				data_c['fid'] = fid[0]
			else:
				print "can't get fid"
				data_c['fid'] = ''
			#-----------------get date-------------------------------------
			date = re.findall('<td.+?>([0-9]{2}-[0-9]{2}).+?</td>',info,re.S)
			if len(date)>0:
				data_c['date'] = date[0]
			else:
				print "can't get date"
				data_c['date'] = ''
			#------------------get team name-------------------------------
			team = re.findall('<a class="team_link".+?>(.+?)</a>',info,re.S)
			if len(team) == 2:
				data_c['team'] = [t.encode('unicode_escape').decode('string_escape') for t in team]
			else:
				print "team name error"
				data_c['team'] = ''
			#-------------------get competition info----------------------
			scene = re.findall('<input.+?'+fid[0]+'.+?>(.+?)</label>',info,re.S)
			if len(scene) == 1:
				data_c['scene'] = scene[0].encode('unicode_escape').decode('string_escape')
			else:
				print "scene error"
				data_c['scene'] = ''
			competition_list.append(data_c)
		return competition_list
	
	def get_company(self,fid):
		company_list = []
		html_company = '-1'
		data_raw = ''
		i = 0
		while html_company!='':
			data_url = 'http://odds.500.com/fenxi1/ouzhi.php?id='+fid+'&ctype=1&start='+str(i*30+1)+'&r=1&style=0&guojia=0&chupan=1'
			try:
				html_company = requests.get(data_url).text.encode('utf8')
			except:
				print "can't open "+data_url
				raise urlOpenError
			data_raw = data_raw+html_company
			i = i+1
			#break #--------------------------------------------------
		re_str = '<p>(.+?)</p>.+?<p>(.+?)</p>.+?<table(.+?)</table>.+?<table(.+?)</table>.+?<table(.+?)</table>.+?<table(.+?)</table>'
		data_split = re.findall(re_str,data_raw,re.S)
		for data_temp in data_split:
			company_dir = {}
			cid = re.findall('id="ck(.+?)"',data_temp[0],re.S)
			if len(cid)==1:
				company_dir['cid'] = cid[0]
			else:
				company_dir['cid'] = ''
			company_dir['compensation'] = re.findall('<td.+?>(.+?)</td>',data_temp[2],re.S)
			company_dir['compensation_change'] = 'class="bg-a"'in data_temp[2] or 'class="bg-b"'in data_temp[2]
			company_dir['kelly'] = re.findall('<td.+?>(.+?)</td>',data_temp[5],re.S)
			company_dir['kelly_change'] = 'class="bg-a"'in data_temp[5] or 'class="bg-b"'in data_temp[5]
			company_list.append(company_dir)
		return company_list
	
	def get_history_kelly(self,fid,cid):
		t_day = time.strftime(time_day, time.localtime( time.time()))
		t_time = time.strftime(time_time, time.localtime( time.time()))
		time_d = t_day+'+'+urllib.quote(t_time)
		kelly_url = 'http://odds.500.com/fenxi1/json/ouzhi.php?type=kelly&r=1&fid='+str(fid)+'&cid='+str(cid)+'&time='+time_d
		try:
			html_h_kelly = requests.get(kelly_url).text.encode('utf8')
		except:
			print "can't open "+kelly_url
			raise urlOpenError
		h_kellt_data = re.findall('\[(\[.+?\])',html_h_kelly,re.S)
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

	file_name = time.strftime(time_day, time.localtime( time.time()))
	clock = time.strftime(time_time, time.localtime( time.time()))
	file_name = 'data/'+file_name+'.xls'
	if int(clock[0:2])<12:
		func = mulprocess_fun_am
		Wt = 'w'
	else:
		func = mulprocess_fun_pm
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
			print i
			if i == proc_amout:
				writeExcl.write_excl(data_output,file_name,Wt)
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
