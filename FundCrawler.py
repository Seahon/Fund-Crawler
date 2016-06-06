#/!usr/bin/python
# -*- coding:utf-8 -*- 
import urllib.request
import re
import datetime
import pymysql
from PyFmter import align

def getHtml(url):
	try:
		page = urllib.request.urlopen(url)
		html = page.read().decode("gb18030")
		return html
	except urllib.request.URLError as e:
		if hasattr(e, "code"):
			print(e.code)
		if hasattr(e, "reason"):
			print(e.reason)

def getFundInfo(html):
	re_str = r'(\d{4}-\d{2}-\d{2}|\d\.\d{3}|-?\d\.\d{2}%)'
	re_pat = re.compile(re_str)
	result = re.findall(re_pat, html)
	return result
	
conn = pymysql.connect(user='root', passwd='123456', host='localhost', db='fund_analysis', charset='utf8')
cur = conn.cursor()
cur.execute('SELECT * FROM product;')
FundInfo = cur.fetchall()

dlDatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print('------ %s ------' % dlDatetime)

# tdy = datetime.datetime.now().strftime('%Y-%m-%d')								# 当日
# ldy = (datetime.datetime.now()+datetime.timedelta(-2)).strftime('%Y-%m-%d')		# 前天
	
for i in range(len(FundInfo)):
	info = dict(zip(['code','name','type'], FundInfo[i]))
	url = 'http://www.chinaamc.com/fund/%(code)s/index.shtml' % info
	html = getHtml(url)
	fundinfo = getFundInfo(html)
	date, price, rate = fundinfo[:3]
	price = float(price)
	rate = float(rate[:-1])/100
	
	# if date==tdy or date==ldy:
	cur.execute("SELECT * FROM record WHERE Date = '%s' AND ProdCode = '%s'" % (date, info['code']))
	rec = cur.fetchall()
	if len(rec)==0:
		cur.execute("INSERT INTO record(Date, ProdCode, Price, Rate) values('%s', '%s', %f, %f);" % (date, info['code'], price, rate))
		conn.commit()
		print('%s%s@%s' % (align(info['name'], 24), align('成功获取数据',14), date))
	else:
		print('%s%s@%s' % (align(info['name'], 24), align('数据已存在', 14), date))
	#else:
	#	print('%s\t\t当天数据不存在' % info['name'])
		
cur.close()
conn.close()