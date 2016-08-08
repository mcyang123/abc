# -*- coding: utf-8 -*-

import xlrd
import xlwt
import xlutils.copy as xlscopy
#data = xlrd.open_workbook(r'D:\project\python\read_excel_modify_word\word2.xlsx')

def write_excl(dataInput,filename,wType):
	'''
	creat an excl file ,dataInput will be writed to filename.xls. wType tell python how to write.
	'''
	if dataInput == '' or filename == '' or wType == '':
		raise fileOpenError('''
			dataInput or fileme or wType is empty.
			''')
	f_c = open(r'target.txt','r')
	target_list = {}
	for s in f_c:
		ss = s.split(':')
		target_list[ss[1].strip()] = ss[0]
	target_id = target_list.keys()
	f_c.close()

	if wType == 'w':
		workbook = xlwt.Workbook(encoding='utf8')    #创建exclwoekbook
		sheet = workbook.add_sheet('AM')         #创建sheet
		sheet2 = workbook.add_sheet('PM')         #创建sheet
		dataInputKeys = dataInput.keys()
		dataInputKeys.sort()
		i = 0
		for k in dataInputKeys:
			#sheet.write(i,0,dataInput[k]['team'].decode('gbk'))
			sheet.write(i,0,dataInput[k]['team'][0].decode('gbk'))
			sheet.write(i,1,'VS')
			sheet.write(i,2,dataInput[k]['team'][1].decode('gbk'))
			sheet.write(i+1,0,target_list[dataInput[k]['cid']])
			sheet.write(i+2,0,dataInput[k]['compensation'][0])
			sheet.write(i+2,1,dataInput[k]['compensation'][1])
			sheet.write(i+2,2,dataInput[k]['compensation'][2])
			sheet.write(i+2,4,dataInput[k]['kelly'][0])
			sheet.write(i+2,5,dataInput[k]['kelly'][1])
			sheet.write(i+2,6,dataInput[k]['kelly'][2])
			i = i+7
		workbook.save(filename)

	if wType == 'a':
		try:
			oldWorkBook = xlrd.open_workbook(filename)
			workbook = xlscopy.copy(oldWorkBook)
			sheet = workbook.get_sheet(1)
		except:
			workbook = xlwt.Workbook(encoding='utf8')    #创建exclwoekbook
			sheet = workbook.add_sheet('PM')         #创建sheet

		dataInputKeys = dataInput.keys()
		dataInputKeys.sort()
		i = 0
		for k in dataInputKeys:
			#sheet.write(i,0,dataInput[k]['team'].decode('gbk'))
			sheet.write(i,0,dataInput[k]['team'][0].decode('gbk'))
			sheet.write(i,1,'VS')
			sheet.write(i,2,dataInput[k]['team'][1].decode('gbk'))
			sheet.write(i+1,0,target_list[dataInput[k]['cid']])
			sheet.write(i+2,0,dataInput[k]['compensation'][0])
			sheet.write(i+2,1,dataInput[k]['compensation'][1])
			sheet.write(i+2,2,dataInput[k]['compensation'][2])
			sheet.write(i+2,4,dataInput[k]['kelly'][0])
			sheet.write(i+2,5,dataInput[k]['kelly'][1])
			sheet.write(i+2,6,dataInput[k]['kelly'][2])
			i = i+7
		workbook.save(filename)

if __name__ == '__main__':
	'''
	f = open('data/2016-08-07-pm.txt','r')
	exec(f.read())
	f.close()
	write_excl(data,'01.xls','a')
	'''





