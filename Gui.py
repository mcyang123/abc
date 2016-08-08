# -*- coding: utf-8 -*-
import sys
import os
from PyQt4 import QtCore,QtGui


Gf_c = open(r'target.txt','r')
Gtarget_list = {}
for Gs in Gf_c:
	Gss = Gs.split(':')
	Gtarget_list[Gss[1].strip()] = Gss[0]
Gtarget_id = Gtarget_list.keys()
Gf_c.close()

class Mywin(QtGui.QWidget):
	def __init__(self):
		super(Mywin,self).__init__()
		self.setWindowTitle('spider')
		self.resize(700,700)

		label1 = QtGui.QLabel(u'选择日期')
		label1.setMargin(10)
		#label2 = QtGui.QLabel(u'选择比赛')
		#label2.setMargin(10)

		self.buttonOK = QtGui.QPushButton(u'显示数据')
		self.buttonStar = QtGui.QPushButton(u'启动爬虫')

		self.textArea = QtGui.QTextEdit()

		#self.checkbox1 = QtGui.QCheckBox(u'显示全部')


		#menu = QtGui.QMenuBar()
		#menu.addAction('&File')
		data_list = os.listdir('data/')
		self.comboboxDay = QtGui.QComboBox()
		for s in data_list:
			self.comboboxDay.addItem(s[0:-4])
		#self.comboboxCompetition = QtGui.QComboBox()
		#self.comboboxCompetition.addItem("all")
		#self.list_change()

		#---------------------布局-----------------------------
		mainLayout = QtGui.QGridLayout()    #全局布局
		mainLayout.addWidget(label1,0,0)
		mainLayout.addWidget(self.comboboxDay,0,1)
		#mainLayout.addWidget(label2,1,0)
		#mainLayout.addWidget(self.comboboxCompetition,1,1)
		mainLayout.addWidget(self.buttonOK,3,0)
		#mainLayout.addWidget(self.buttonStar,20,0)
		#mainLayout.addWidget(self.checkbox1,3,1)
		mainLayout.addWidget(self.textArea,0,2,20,1)

		self.setLayout(mainLayout)
		self.connect(self.buttonOK, QtCore.SIGNAL('clicked()'),self.output)
		#self.connect(self.buttonStar, QtCore.SIGNAL('clicked()'),self.star)
		#self.connect(self.comboboxDay,QtCore.SIGNAL('activated(QString)'),self.list_change)
		#label.setAlignment(QtCore.Qt.AlignCenter)
		#self.setCentralWidget(label)
	def output(self):
		global target_list
		data_file = str(self.comboboxDay.currentText())
		#Competition = str(self.comboboxCompetition.currentText())
		#display_all = self.checkbox1.checkState
		data_list = os.listdir('data/')
		if data_file == '':
			pass
		elif data_file+'.txt' in data_list:
			try :
				f = open('data/'+data_file+'.txt','r')
				data_text = f.read()
				exec(data_text)
				f.close()
			except:
				pass
			#if Competition == 'all':
			data_key = data.keys()
			data_key.sort()
			ss = u'共获取'+str(len(data_key))+u'条数据：'+'\n'
			for k in data_key:
				d = data[k]
				com = str(d['compensation'])
				com = com[1:24].replace("'",'')
				kel = str(d['kelly'])
				kel = kel[1:24].replace("'",'')
				ss = ss + d['scene'].decode('gbk') +'    '                      #场次
				ss = ss + d['team'].decode('gbk') +'\n'                       #队伍
				ss = ss + u'公司:'+Gtarget_list[d['cid']].decode('gbk') +'\n'           #公司
				ss = ss + u'赔率:'+com +'\n'                                           #赔率
				ss = ss + 'kelly:'+kel+'\n\n'                                          #kelly
			self.textArea.setText(ss)    #display
			#else:
			#	self.textArea.setText()    #display
		else:
			self.textArea.setText('no such file!')

	def list_change(self):
		data_file = str(self.comboboxDay.currentText())
		#try:
		f = open('data/'+data_file+'.txt','r')
		data_text = f.read()
		exec(data_text)
		f.close()
		for d in data:
			self.comboboxCompetition.addItem(d['team'].decode('gbk'))    #去重
		#except:
			#pass

	def star(self):
		print '123'
		import getinfo
		#getinfo.star_spider()
		print 'star'
		self.comboboxCompetition.addItem(u'爬虫已启动')

app = QtGui.QApplication(sys.argv)
mywin = Mywin()
mywin.show()
app.exec_()