# -*- coding: utf-8 -*-
#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
import urllib.parse
from threading import Thread
import threading
import urllib.request
import json
import configparser
import string, os, sys
import re
import platform
import time
import socket
from time import sleep
Pstart =time.time()
print("初始化中....")
socket.setdefaulttimeout(10)
root_dir = os.path.dirname(__file__)  # 获取当前文件所在目录的上一级目录，即项目所在目录E:\Crawler
Conf = configparser.ConfigParser()

if platform.system().lower() == 'windows':
	Conf.read(root_dir+"\TiebaGuardian_Config.ini",encoding="utf-8")
	print("运行在Windows系统下")
	print (root_dir+"\TiebaGuardian_Config.ini") #文件路径
	OperateTargetListStored = open(root_dir+"\TiebaGuardian_OptRec.txt","a",encoding="utf-8")

if platform.system().lower() == 'linux':
	Conf.read(root_dir+"/TiebaGuardian_Config.ini",encoding="utf-8")
	print("运行在Linux系统下")
	print (root_dir+"/TiebaGuardian_Config.ini") #文件路径
	OperateTargetListStored = open(root_dir+"/TiebaGuardian_OptRec.txt","a",encoding="utf-8")

OperateTargetJSON = []
OperateTemp = {"Name":"null","Weight":"null","Reason":"null","Type":"null"}
Ties = {}
BDUSS = Conf.get("Account","BDUSS")
TargetBa = Conf.get("Settings","TargetBa")
ScanRange = Conf.getint("Settings","ScanRange")
ScanMode = Conf.getint("Settings","ScanMode")
ReadOnly = Conf.getboolean("Settings","ReadOnly")
BanDayTimeLimit = Conf.getint("Settings","BanDayTimeLimit")
BanReason = Conf.get("Settings","BanReason")
BlackList = Conf.get("Protect","BlackList").split("^")
WhiteList = Conf.get("Protect","WhiteList").split("^")
BlackKeyWords = Conf.get("Protect","BlackKeyWords").split("^")
WhiteKeyWords = Conf.get("Protect","WhiteKeyWords").split("^")
###对于帖子的判断
Tie_ContentLength_Limit = Conf.getint("Protect","Tie_ContentLength_Limit")
Reply_ContentLength_Limit = Conf.getint("Protect","Reply_ContentLength_Limit")
TieFrequence_Limit = Conf.getint("Protect","TieFrequence_Limit")
TieFrequence_Interval_time = Conf.getint("Protect","TieFrequence_Interval_time")
TieFrequence_Instant_BAN = Conf.getboolean("Protect","TieFrequence_Instant_BAN")
TieExactQuantityLimit = Conf.getint("Protect","TieExactQuantityLimit")
###对于用户的判断
Member_Fans_Limit = Conf.getint("Protect","Member_Fans_Limit")
Member_historyTie_QuantityLimit = Conf.getint("Protect","Member_historyTie_QuantityLimit")
Member_Subs_Limit = Conf.getint("Protect","Member_Subs_Limit")
###权值计算
BlackKeyWords_Weight = Conf.getfloat("Protect","BlackKeyWords_Weight")
WhiteKeyWords_MinusWeight = - Conf.getfloat("Protect","WhiteKeyWords_MinusWeight")

Member_LimitWeight_per_item = Conf.getfloat("Weight","Member_LimitWeight_per_item")
Tie_LimitWeight_per_item = Conf.getfloat("Weight","Tie_LimitWeight_per_item")

DeleteTie_Total = Conf.getfloat("Weight","DeleteTie_Total")
Ban_Total = Conf.getfloat("Weight","Ban_Total")
###Function
def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
def getTbs():
	TbsReq = urllib.request.Request("http://tieba.baidu.com/dc/common/tbs",headers=BDUSSheader)
	TbsOr = urllib.request.urlopen(TbsReq).read()
	Tbs = json.loads(TbsOr.decode("utf-8"))["tbs"]
	#print(json.loads(TbsOr.decode("utf-8"))["is_login"])
	return Tbs
def getFid(Baname):
	FidReq = urllib.request.Request("http://tieba.baidu.com/f/commit/share/fnameShareApi?ie=utf-8&fname=" + urllib.parse.quote(Baname))
	FidOr = urllib.request.urlopen(FidReq).read()
	Fid = json.loads(FidOr.decode("utf-8"))["data"]["fid"]
	#print(json.loads(TbsOr.decode("utf-8"))["is_login"])
	return Fid
def Is_in_WhiteList(str):
	for temp in WhiteList:
		if(str == temp):
			return True
	return False
def Is_in_BlackList(str):
	for temp in BlackList:
		if(str == temp):
			return True
	return False
@async
def TieDetailGet(TidList):
	for tempd in TidList:
		ErrorOccured = False
		try:
			TieReq = urllib.request.Request("http://tieba.baidu.com/mg/p/getPbData?kz="+str(tempd))
			TieOr = urllib.request.urlopen(TieReq).read()
			TieDetail = json.loads(TieOr.decode("utf-8"))["data"]["post_list"]
		except:
			TieDetail = {"Error":"Error"}
			ErrorOccured = True
		bg = 0
		for tempv in TieDetail:
			for tempx in Ties:
				if ErrorOccured:
					Ties[tempx]["Content"] = "error"
					break
				if ((Ties[tempx]["tid"] == tempd) and ("content" in tempv)):
					if (tempv["content"][0]):
						if ("text" in tempv["content"][0]):
							Ties[tempx]["Content"] = Ties[tempx]["Content"] + tempv["content"][0]["text"].replace("<br/>","")
			bg=bg+1
	return 0
@async
def AuthorDetailGet(tempx):
	if(Authors[tempx]["name"] == None):
		Authors[tempx]["HistoryTieCount"] = -1
		Authors[tempx]["SubsCount"] = -1
		Authors[tempx]["FansCount"] = -1
		return
	if "tb." not in Authors[tempx]["name"]:
		headerb["Referer"] = headerb["Referer"] + str(Authors[tempx]["posts"][0])
		AuthorReq = urllib.request.Request("http://tieba.baidu.com/home/main?un=" + urllib.parse.quote(Authors[tempx]["name"]),headers=headerb)
		try:
			AuthorOr = urllib.request.urlopen(AuthorReq).read()
		except:
			try:
				AuthorOr = urllib.request.urlopen(AuthorReq).read()
				print("获取用户"+Authors[tempx]["name"]+"详细信息时发生错误，正在重试")
			except:
				try:
					AuthorOr = urllib.request.urlopen(AuthorReq).read()
					print("获取用户"+Authors[tempx]["name"]+"详细信息时再次发生错误，正在重试")
				except:
					print("获取用户"+Authors[tempx]["name"]+"详细信息失败，不再尝试获取")
					Authors[tempx]["HistoryTieCount"] = -1
					Authors[tempx]["SubsCount"] = -1
					Authors[tempx]["FansCount"] = -1
					return
		AuthorDEC = AuthorOr.decode("utf-8")
		AuthorTieCount =  re.findall(r'home_tab_item_num">(.*?)</',AuthorDEC)[0]
		AuthorSubs = re.findall(r'home_tab_item_num">(.*?)</',AuthorDEC)[2]
		AuthorFans = re.findall(r'home_tab_item_num">(.*?)</',AuthorDEC)[3]
		if ("万" in AuthorTieCount):
			AuthorTieCount = AuthorTieCount.replace("万","")
			AuthorTieCount = float(AuthorTieCount) * 10000
		Authors[tempx]["HistoryTieCount"] = int(AuthorTieCount)
		if ("万" in AuthorSubs):
			AuthorSubs = AuthorSubs.replace("万","")
			AuthorSubs = float(AuthorSubs) * 10000
		Authors[tempx]["SubsCount"] = int(AuthorSubs)
		if ("万" in AuthorFans):
			AuthorFans = AuthorFans.replace("万","")
			AuthorFans = float(AuthorFans) * 10000
		Authors[tempx]["FansCount"] = int(AuthorFans)
	else:
		Authors[tempx]["HistoryTieCount"] = -1
		Authors[tempx]["SubsCount"] = -1
		Authors[tempx]["FansCount"] = -1
def AddIntoRecList(name = "null",weight= "null",reason = "null",type = 0):
	if type == 0:
		OperateTemp["Name"] = name
		OperateTemp["Weight"] = weight
		OperateTemp["Reason"] = reason
		OperateTemp["Type"] = "封禁"
		OperateTargetJSON.append(json.dumps(OperateTemp))
		pass
	if type == 1:
		OperateTemp["Name"] = name
		OperateTemp["Reason"] = reason
		OperateTemp["Type"] = "删帖"
		OperateTargetJSON.append(json.dumps(OperateTemp))
	if type == 2:
		OperateTemp["Name"] = name
		OperateTemp["Weight"] = weight
		OperateTemp["Reason"] = reason
		OperateTemp["Type"] = "封禁且删帖"
		OperateTargetJSON.append(json.dumps(OperateTemp))
	pass
def TOperate(optype,TreadID,TargetMember="Null",ReasonBan = BanReason,Bandays = BanDayTimeLimit,BanWeight = 0.0,Weight = 0,replyobj = object()):
	if(optype == 0 and negation_bool(ReadOnly)):#删帖 需要TreadID[list]
		if(not TreadID):
			return 0
		separator = '_'
		data_joined = separator.join(TreadID)
		Sheader["Referer"] = "http://tieba.baidu.com/p/" + str(TreadID)
		Tbs = getTbs()
		Fid = getFid(TargetBa)
		Data = {
			"ie":"utf-8",
			"fid":Fid,
			"tbs":Tbs,
			"tid":data_joined,
			"kw":TargetBa
			}
		DataFinal = urllib.parse.urlencode(Data).encode('utf-8')
		TOperateReq = urllib.request.Request("http://tieba.baidu.com/f/commit/thread/batchDelete ",DataFinal,Sheader)
		TOperateOr = urllib.request.urlopen(TOperateReq).read()
		TOperateResult = json.loads(TOperateOr.decode("utf-8"))
		return TOperateResult
	elif(optype == 1 and negation_bool(ReadOnly)):#封禁 需要TargetMember
		if(TargetMember == "Null"):
			return 0
		if("tb." not in TargetMember):
			Sheader["Referer"] = "http://tieba.baidu.com/bawu2/platform/listMember?word=" + urllib.parse.quote(TargetBa)
			if("<Weight>" in ReasonBan):
				ReasonBan = ReasonBan.replace("<Weight>",str(BanWeight))
			Tbs = getTbs()
			Fid = getFid(TargetBa)
			Data = {
				"day":str(Bandays),
				"fid":Fid,
				"tbs":Tbs,
				"ie":"utf-8",
				"user_name[]":TargetMember,
				"reason":ReasonBan
				}
			DataFinal = urllib.parse.urlencode(Data).encode("utf-8")
			TOperateReq = urllib.request.Request("http://tieba.baidu.com/pmc/blockid",DataFinal,Sheader)
			TOperateOr = urllib.request.urlopen(TOperateReq).read()
			TOperateResult = json.loads(TOperateOr.decode("utf-8"))
		else:
			Sheader["Referer"] = "http://tieba.baidu.com/bawu2/platform/listMember?word=" + urllib.parse.quote(TargetBa)
			if("<Weight>" in ReasonBan):
				ReasonBan = ReasonBan.replace("<Weight>",str(BanWeight))
			Tbs = getTbs()
			Fid = getFid(TargetBa)
			Data = {
				"day":str(Bandays),
				"fid":Fid,
				"tbs":Tbs,
				"ie":"utf-8",
				"portrait[]":TargetMember,
				"reason":ReasonBan
				}
			DataFinal = urllib.parse.urlencode(Data).encode("utf-8")
			TOperateReq = urllib.request.Request("http://tieba.baidu.com/pmc/blockid",DataFinal,Sheader)
			TOperateOr = urllib.request.urlopen(TOperateReq).read()
			TOperateResult = json.loads(TOperateOr.decode("utf-8"))
		return TOperateResult 
	elif(optype == 2 and negation_bool(ReadOnly)):#封禁并删帖 需要TreadID[list] 和 TargetMember
		if(not TreadID):
			return 0
		if(TargetMember == "Null"):
			return 0

		if("tb." not in TargetMember):
			Sheader["Referer"] = "http://tieba.baidu.com/bawu2/platform/listMember?word=" + urllib.parse.quote(TargetBa)
			if("<Weight>" in ReasonBan):
				ReasonBan = ReasonBan.replace("<Weight>",str(BanWeight))
			Tbs = getTbs()
			Fid = getFid(TargetBa)
			Data = {
				"day":str(Bandays),
				"fid":Fid,
				"tbs":Tbs,
				"ie":"utf-8",
				"user_name[]":TargetMember,
				"reason":ReasonBan
			}
			DataFinal = urllib.parse.urlencode(Data).encode("utf-8")
			TOperateReq = urllib.request.Request("http://tieba.baidu.com/pmc/blockid",DataFinal,Sheader)
			TOperateOr = urllib.request.urlopen(TOperateReq).read()
			TOperateResult = str(json.loads(TOperateOr.decode("utf-8")))
		else:
			Sheader["Referer"] = "http://tieba.baidu.com/bawu2/platform/listMember?word=" + urllib.parse.quote(TargetBa)
			if("<Weight>" in ReasonBan):
				ReasonBan = ReasonBan.replace("<Weight>",str(BanWeight))
			Tbs = getTbs()
			Fid = getFid(TargetBa)
			Data = {
				"day":str(Bandays),
				"fid":Fid,
				"tbs":Tbs,
				"ie":"utf-8",
				"portrait[]":TargetMember,
				"reason":ReasonBan
			}
			DataFinal = urllib.parse.urlencode(Data).encode("utf-8")
			TOperateReq = urllib.request.Request("http://tieba.baidu.com/pmc/blockid",DataFinal,Sheader)
			TOperateOr = urllib.request.urlopen(TOperateReq).read()
			TOperateResult = str(json.loads(TOperateOr.decode("utf-8")))
		separator = '_'
		data_joined = separator.join(TreadID)
		Sheader["Referer"] = "http://tieba.baidu.com/p/" + str(TreadID)
		Tbs = getTbs()
		Fid = getFid(TargetBa)
		Data = {
			"ie":"utf-8",
			"fid":Fid,
			"tbs":Tbs,
			"tid":data_joined,
			"kw":TargetBa
			}
		DataFinal = urllib.parse.urlencode(Data).encode('utf-8')
		TOperateReq = urllib.request.Request("http://tieba.baidu.com/f/commit/thread/batchDelete ",DataFinal,Sheader)
		TOperateOr = urllib.request.urlopen(TOperateReq).read()
		TOperateResultTotal = TOperateResult + str(json.loads(TOperateOr.decode("utf-8")))


		return TOperateResultTotal
	elif(optype == 3):#对帖子增加权值
		for tempa in Ties:
			for tempc in TreadID:
				if(str(Ties[tempa]["tid"]) == str(tempc)):
					Ties[tempa]["Weight"] = Ties[tempa]["Weight"] + Weight
		return 3
	elif(optype == 4):#对作者增加权值
		for tempb in Authors:
			if(Authors[tempb]["name"] == TargetMember):
				Authors[tempb]["Weight"] = Authors[tempb]["Weight"] + Weight
		return 4
	elif(optype == 5):#对回复楼增加权值
		for tempa in Reply:
			for tempc in TreadID:
				if(str(Reply[tempa]["pid"]) == str(tempc)):
					Reply[tempa]["Weight"] = Reply[tempa]["Weight"] + Weight
		return 5
	elif(optype == 6):#对回复楼作者增加权值
		for tempb in RPAuthors:
			if(RPAuthors[tempb]["name"] == TargetMember):
				RPAuthors[tempb]["Weight"] = RPAuthors[tempb]["Weight"] + Weight
		return 6
	elif(optype == 8 and negation_bool(ReadOnly)):#删除回复楼
		if(not replyobj.tid and not replyobj.pid):
			return 0
		Sheader["Referer"] = "http://tieba.baidu.com/p/" + str(replyobj.tid)
		Tbs = getTbs()
		Fid = getFid(TargetBa)
		Data = {
			"commit_fr":"pb",
			"ie":"utf-8",
			"fid":Fid,
			"tbs":Tbs,
			"tid":replyobj.tid,
			"kw":TargetBa,
			"pid":replyobj.pid
			}
		DataFinal = urllib.parse.urlencode(Data).encode('utf-8')
		TOperateReq = urllib.request.Request("http://tieba.baidu.com/f/commit/post/delete ",DataFinal,Sheader)
		TOperateOr = urllib.request.urlopen(TOperateReq).read()
		TOperateResult = json.loads(TOperateOr.decode("utf-8"))
		return TOperateResult
	else:
		return 9
def negation_bool(b):
  b = bool(1 - b)
  return b
def FilterReplyHtml(html):
	tempQ= re.findall(r"data-field='(?={&quot;author&quot;)(.*?)' data-pid",html)
	tempC = []
	q = 0
	for i in tempQ:
		tempC.append(tempQ[q].replace("&quot;",'"').replace("&lt;",'<').replace("&gt;",'>').replace("&nbsp;",' ').replace("&amp;",'&'))
		q = q + 1
	return tempC
def ScanReplyPn(html):
	tempQ = re.findall(r"共(.*?)页",html)
	tempC = re.findall(r"\d+",tempQ[0])
	return int(tempC[0])
@async
def GetReplyDetail(i):
	try:
		ReplyReq = urllib.request.Request("https://tieba.baidu.com/p/"+ str(Ties[i]["tid"]) + "?pn=" + str(1) + "&ajax=1",headers=Replyheader)
		ReplyOr = urllib.request.urlopen(ReplyReq).read()
	except:
		try:
			print("读取第"+str(i)+"个帖子的第1页HTML时出错，重试。")
			ReplyReq = urllib.request.Request("https://tieba.baidu.com/p/"+ str(Ties[i]["tid"]) + "?pn=" + str(1) + "&ajax=1",headers=Replyheader)
			ReplyOr = urllib.request.urlopen(ReplyReq).read()
		except:
			print("读取第"+str(i)+"个帖子的第1页HTML时出错，再次重试。")
			ReplyReq = urllib.request.Request("https://tieba.baidu.com/p/"+ str(Ties[i]["tid"]) + "?pn=" + str(1) + "&ajax=1",headers=Replyheader)
			ReplyOr = urllib.request.urlopen(ReplyReq).read()
	result = ReplyOr.decode("utf-8")
	html1 = result
	pn = ScanReplyPn(html1)
	pb = 1
	while(pb<=pn):
		try:
			ReplyReq = urllib.request.Request("https://tieba.baidu.com/p/"+ str(Ties[i]["tid"]) + "?pn=" + str(pb) + "&ajax=1",headers=Replyheader)
			ReplyOr = urllib.request.urlopen(ReplyReq).read()
		except:
			try:
				print("读取第"+str(i)+"个帖子的第"+str(pb)+"页HTML时出错，重试。")
				ReplyReq = urllib.request.Request("https://tieba.baidu.com/p/"+ str(Ties[i]["tid"]) + "?pn=" + str(pb) + "&ajax=1",headers=Replyheader)
				ReplyOr = urllib.request.urlopen(ReplyReq).read()
			except:
				print("读取第"+str(i)+"个帖子的第"+str(pb)+"页HTML时出错，再次重试。")
				ReplyReq = urllib.request.Request("https://tieba.baidu.com/p/"+ str(Ties[i]["tid"]) + "?pn=" + str(pb) + "&ajax=1",headers=Replyheader)
				ReplyOr = urllib.request.urlopen(ReplyReq).read()
		result = ReplyOr.decode("utf-8")
		html2.append(result)
		pb = pb + 1
	return 1
@async
def RPAuthorDetailGet(tempx):
	if(RPAuthors[tempx]["name"] == None):
		RPAuthors[tempx]["HistoryTieCount"] = -1
		RPAuthors[tempx]["SubsCount"] = -1
		RPAuthors[tempx]["FansCount"] = -1
		return
	if "tb." not in RPAuthors[tempx]["name"]:
		headerb["Referer"] = headerb["Referer"] + str(RPAuthors[tempx]["pids"][0])
		AuthorReq = urllib.request.Request("http://tieba.baidu.com/home/main?un=" + urllib.parse.quote(RPAuthors[tempx]["name"]),headers=headerb)
		try:
			AuthorOr = urllib.request.urlopen(AuthorReq).read()
		except:
			try:
				AuthorOr = urllib.request.urlopen(AuthorReq).read()
				print("获取用户"+RPAuthors[tempx]["name"]+"详细信息时发生错误，正在重试")
			except:
				try:
					AuthorOr = urllib.request.urlopen(AuthorReq).read()
					print("获取用户"+RPAuthors[tempx]["name"]+"详细信息时再次发生错误，正在重试")
				except:
					print("获取用户"+RPAuthors[tempx]["name"]+"详细信息失败，不再尝试获取")
					RPAuthors[tempx]["HistoryTieCount"] = -1
					RPAuthors[tempx]["SubsCount"] = -1
					RPAuthors[tempx]["FansCount"] = -1
					return
		AuthorDEC = AuthorOr.decode("utf-8")
		AuthorTieCount =  re.findall(r'home_tab_item_num">(.*?)</',AuthorDEC)[0]
		AuthorSubs = re.findall(r'home_tab_item_num">(.*?)</',AuthorDEC)[2]
		AuthorFans = re.findall(r'home_tab_item_num">(.*?)</',AuthorDEC)[3]
		if ("万" in AuthorTieCount):
			AuthorTieCount = AuthorTieCount.replace("万","")
			AuthorTieCount = float(AuthorTieCount) * 10000
		RPAuthors[tempx]["HistoryTieCount"] = int(AuthorTieCount)
		if ("万" in AuthorSubs):
			AuthorSubs = AuthorSubs.replace("万","")
			AuthorSubs = float(AuthorSubs) * 10000
		RPAuthors[tempx]["SubsCount"] = int(AuthorSubs)
		if ("万" in AuthorFans):
			AuthorFans = AuthorFans.replace("万","")
			AuthorFans = float(AuthorFans) * 10000
		RPAuthors[tempx]["FansCount"] = int(AuthorFans)
	else:
		RPAuthors[tempx]["HistoryTieCount"] = -1
		RPAuthors[tempx]["SubsCount"] = -1
		RPAuthors[tempx]["FansCount"] = -1
@async
def DeleteReply(replyobj):
	if(negation_bool(ReadOnly)):#删除回复楼
		if(not replyobj.tid and not replyobj.pid):
			return 0
		Sheader["Referer"] = "http://tieba.baidu.com/p/" + str(replyobj.tid)
		Tbs = getTbs()
		Fid = getFid(TargetBa)
		Data = {
			"commit_fr":"pb",
			"ie":"utf-8",
			"fid":Fid,
			"tbs":Tbs,
			"tid":replyobj.tid,
			"kw":TargetBa,
			"pid":replyobj.pid
			}
		DataFinal = urllib.parse.urlencode(Data).encode('utf-8')
		TOperateReq = urllib.request.Request("http://tieba.baidu.com/f/commit/post/delete ",DataFinal,Sheader)
		TOperateOr = urllib.request.urlopen(TOperateReq).read()
		TOperateResult = json.loads(TOperateOr.decode("utf-8"))
		return TOperateResult
pass
###配置读取完毕,验证BDUSS
BDUSSheader = {
     'Connection': 'keep-alive',
     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
	 'Cookie':'BDUSS='+ BDUSS
}
Sheader = { 
	"Host": "tieba.baidu.com",
	"Origin": "http://tieba.baidu.com",
	'Connection': 'keep-alive',
	"Accept": "application/json, text/javascript, */*; q=0.01",
	"X-Requested-With": "XMLHttpRequest",
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36", 
	"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
	"Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
	"Referer": "http://tieba.baidu.com/",
	'Cookie':'BDUSS='+ BDUSS
}
Replyheader = { 
	"Host": "tieba.baidu.com",
	"Origin": "http://tieba.baidu.com",
	'Connection': 'keep-alive',
	"Accept": "application/json, text/javascript, */*; q=0.01",
	"X-Requested-With": "XMLHttpRequest",
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36", 
	"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
	"Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
	"Referer": "http://tieba.baidu.com/",
	'Cookie':'BDUSS='+ BDUSS
}
BDUSSreq = urllib.request.Request("http://i.baidu.com/",headers=BDUSSheader)
BDUSSresponse = urllib.request.urlopen(BDUSSreq).read()
BDUSSresponse=BDUSSresponse.decode("utf-8")
#print(BDUSSresponse)
TiebaID = re.findall(r'"username":"(.*?)","iconUrl"',BDUSSresponse)

if  len(TiebaID):
	print("BDUSS检查完毕，贴吧用户名："+TiebaID[0])
else:
	print("BDUSS无效，请检查Config")
	quit(1)
###验证完毕,启动主程序
print("全部准备工作已完成，主程序准备启动....")
TargetBaUrlOb = urllib.request.Request("http://tieba.baidu.com/mg/f/getFrsData?kw="+urllib.parse.quote(TargetBa)+"&rn="+str(ScanRange)+"&pn=0&is_good=0&cid=0&sort_type="+str(ScanMode)+"&fr=&default_pro=1&only_thread_list=1")
TieOrigin_Data = urllib.request.urlopen(TargetBaUrlOb).read()
TieOrigin_Data = TieOrigin_Data.decode("utf-8") 
TieOrigin_JsonOb = json.loads(TieOrigin_Data)["data"]["thread_list"] #贴吧在扫描范围内的帖子数据
#STEP1/////////////////////////////////////////////////
print("执行Step1>>获取帖子列表")
n=0
for temp in TieOrigin_JsonOb:#初始化帖子列表
	if (temp):
		Ties[n] = {}
		Ties[n]["title"] = temp["title"]
		Ties[n]["shortview"] = temp["abstract"][0]["text"]
		Ties[n]["tid"] = temp["tid"]
		Ties[n]["sendTime"] = temp["create_time"]
		Ties[n]["lastTime"] = temp["last_time_int"]
		if(not "贴吧用户_" in temp["author"]["name_show"]):
			Ties[n]["author"] = temp["author"]["name"]
		else:
			Ties[n]["author"] = "null"
			Ties[n]["id"] = temp["author"]["portrait"]
		Ties[n]["Weight"] = 0
		Ties[n]["Content"] = ""
		n = n + 1
	else:
		break
a=0
Authors = {}
userTempo = {}
Dfound = False
for temp2 in Ties:#对帖子进行分类
	Dfound = False
	if(Ties[temp2]["author"] == 'null'):
		userTempo["id"] = Ties[temp2]["id"]
		userTempo["author"] = "null"
	else:
		userTempo["author"] = Ties[temp2]["author"]
	userTempo["lastTime"] = Ties[temp2]["lastTime"]
	userTempo["createTime"] = Ties[temp2]["sendTime"]
	userTempo["tid"] = Ties[temp2]["tid"]
	bn = 0
	while bn < len(Authors):
		if (Authors[bn]["name"] == (userTempo["author"] if(userTempo["author"]!="null") else userTempo["id"])):
			Authors[bn]["posts"].append(userTempo["tid"])
			Authors[bn]["createTimes"].append(userTempo["createTime"])
			Dfound=True
		bn=bn+1
	if(Dfound == False):
		Authors[bn]={}
		Authors[bn]['name'] = userTempo["author"] if(userTempo["author"]!="null") else userTempo["id"]
		Authors[bn]["posts"] = list()
		Authors[bn]["createTimes"] = list()
		Authors[bn]["posts"].append(userTempo["tid"])
		Authors[bn]["createTimes"].append(userTempo["createTime"])
		Authors[bn]["Weight"] = 0
	a=a+1
#STEP2/////////////////////////////////////////////////
print("执行Step2>>检测发布者发帖相关特征")
bc = 0
Tielisttemp=list()
for temp3 in Authors:
	Tielisttemp=list()
	zipped = zip(Authors[temp3]["posts"],Authors[temp3]["createTimes"])
	sort_zipped = sorted(zipped,key=lambda x:(x[1],x[0]))
	result = zip(*sort_zipped)
	x_axis, y_axis = [list(x) for x in result]
	Authors[temp3]["posts"] = x_axis
	Authors[temp3]["createTimes"] = y_axis
	#对帖子ID与发帖时间这两个list的顺序进行同步排序
	cd = 0
	Min = Authors[temp3]["createTimes"][0] + TieFrequence_Interval_time
	for temp4 in Authors[temp3]["createTimes"]:
		if (temp4 < Min):
			Tielisttemp.append(str(Authors[temp3]["posts"][cd]))
		else:
			Min = temp4 + TieFrequence_Interval_time
		cd=cd+1
	if(len(Tielisttemp) == 1):
		Tielisttemp.clear()
	#print(Tielisttemp)
	if(len(Tielisttemp) >= TieFrequence_Limit):
		if(TieFrequence_Instant_BAN):
			#BAN People and Delete
			print("检测到高频率发言，您已设置立刻封禁,已封禁违规人："+Authors[temp3]["name"])
			print("删除其违规帖子："+str(Tielisttemp))
			if(not Is_in_WhiteList(Authors[temp3]["name"])):
				TOperate(2,Tielisttemp,Authors[temp3]["name"],BanReason,1,999)
				AddIntoRecList(Authors[temp3]["name"],"999","发言频率过高",2)
			else:
				print("违规人"+Authors[temp3]["name"]+"在白名单内，不予处理")
			pass
		else:
			#Increase Weight
			print("检测到高频率发言，增加这些帖子的违规权值,违规人："+Authors[temp3]["name"])
			if(not Is_in_WhiteList(Authors[temp3]["name"])):
				TOperate(4,[],Authors[temp3]["name"],Weight = Tie_LimitWeight_per_item)
				for i in Tielisttemp:
					TOperate(3,i,Weight = Tie_LimitWeight_per_item)
			else:
				print("违规人"+Authors[temp3]["name"]+"在白名单内，不予处理")
			pass
	if(len(Authors[temp3]["posts"]) >= TieExactQuantityLimit):
		print("检测到淹没式低频发言，增加这些帖子的违规权值,违规人："+Authors[temp3]["name"])
		if(not Is_in_WhiteList(Authors[temp3]["name"])):
			TOperate(4,[],Authors[temp3]["name"],Weight = Tie_LimitWeight_per_item)
			for i in Tielisttemp:
				TOperate(3,i,Weight = Tie_LimitWeight_per_item)
		else:
				print("违规人"+Authors[temp3]["name"]+"在白名单内，不予处理")
		pass
	bc=bc+1	
templist = []
for tempx in Authors:
	if(Is_in_BlackList(Authors[tempx]["name"])):
		bg = 0
		for tempa in Authors[tempx]["posts"]:
			templist.append(str(tempa))
			bg=bg+1
		TOperate(2,templist,Authors[tempx]["name"],"您在黑名单中，贴吧守护者已自动对您进行处理，如有异议请询问吧务",1)
		AddIntoRecList(Authors[tempx]["name"],"999","检测到黑名单中记录",2)
		print("检测到黑名单中用户："+Authors[tempx]["name"])
		print("清除其帖子：")
		print(templist)
		templist = []
pass
#STEP3/////////////////////////////////////////////////
print("执行Step3>>遍历帖子内容")
coua = threading.active_count()
for tempx in Authors:
	TieDetailGet(Authors[tempx]["posts"])
cou = threading.active_count()
while(not cou == coua):
	sleep(0.3)
	cou = threading.active_count()
pass
#STEP4/////////////////////////////////////////////////
print("执行Step4>>过滤帖子关键字")
for tempx in Ties:
	for tempz in BlackKeyWords:
		if((tempz in Ties[tempx]["Content"]) or (tempz in Ties[tempx]["title"])):
			TOperate(4,[],TargetMember = Ties[tempx]["author"] if(Ties[tempx]["author"] != "null") else Ties[tempx]["id"],Weight = BlackKeyWords_Weight)
			TOperate(3,[Ties[tempx]["tid"]],Weight = BlackKeyWords_Weight)
	for tempm in WhiteKeyWords:
		if((tempm in Ties[tempx]["Content"]) or (tempm in Ties[tempx]["title"])):
			TOperate(4,[],TargetMember = Ties[tempx]["author"] if(Ties[tempx]["author"] != "null") else Ties[tempx]["id"],Weight = WhiteKeyWords_MinusWeight)
			TOperate(3,[Ties[tempx]["tid"]],Weight = WhiteKeyWords_MinusWeight)
	if (len(Ties[tempx]["Content"]) < Tie_ContentLength_Limit):
			TOperate(4,[],TargetMember = Ties[tempx]["author"] if(Ties[tempx]["author"] != "null") else Ties[tempx]["id"],Weight = Tie_LimitWeight_per_item)
			TOperate(3,[Ties[tempx]["tid"]],Weight = Tie_LimitWeight_per_item)
pass
#STEP5/////////////////////////////////////////////////
RequestFinned = False
Resss = []
print("执行Step5>>查询发布者账号信息")
headerb = {
	"Host": "tieba.baidu.com",
	"Origin": "http://tieba.baidu.com",
	'Connection': 'keep-alive',
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"X-Requested-With": "XMLHttpRequest",
	"User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36", 
	"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
	"Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
	"Referer": "http://tieba.baidu.com/",
	}
for tempx in Authors:
	AuthorDetailGet(tempx)
while(not RequestFinned):
	for i in Authors:
		try:
			Resss.append(Authors[i]["FansCount"])
		except:
			Resss.append(-2)
		try:
			Resss.append(Authors[i]["HistoryTieCount"])
		except:
			Resss.append(-2)
		try:
			Resss.append(Authors[i]["SubsCount"])
		except:
			Resss.append(-2)
	pass
	for a in Resss:
		if(a==-2):
			Resss = []
			RequestFinned = False
			break;
		else:
			RequestFinned = True
pass
for tempx in Authors:
	if (Authors[tempx]["HistoryTieCount"] < Member_historyTie_QuantityLimit):
		TOperate(4,[],Authors[tempx]["name"],Weight = Member_LimitWeight_per_item)
		TOperate(3,Authors[tempx]["posts"],Weight = Member_LimitWeight_per_item)
		pass;
	if (Authors[tempx]["SubsCount"] < Member_Subs_Limit):
		TOperate(4,[],Authors[tempx]["name"],Weight = Member_LimitWeight_per_item)
		TOperate(3,Authors[tempx]["posts"],Weight = Member_LimitWeight_per_item)
		pass;
	if (Authors[tempx]["FansCount"] < Member_Fans_Limit):
		TOperate(4,[],Authors[tempx]["name"],Weight = Member_LimitWeight_per_item)
		TOperate(3,Authors[tempx]["posts"],Weight = Member_LimitWeight_per_item)
		pass;
pass
#STEP6////////////////////////////////////////////////////
Replies= []
Reply = {}
RPoriginJSONstr = []
RPAuthors = {}
html1 = ""
html2 = [] #回复ajax容器
print("执行Step6>>遍历所有帖子的回复HTML")
coua = threading.active_count()
for i in Ties:
	GetReplyDetail(i)
pass
cou = threading.active_count()
while(not cou == coua):
	sleep(0.3)
	cou = threading.active_count()
pass

for i in html2:
	RPoriginJSONstr.extend(FilterReplyHtml(i))
pass

for qz in RPoriginJSONstr:
	Replies.append(json.loads(qz))
pass
#STEP7////////////////////////////////////////////////////
print("执行Step7>>分析所有帖子的回复，共 "+str(len(Replies))+" 条")
a=0
userTempo = {}
Dfound = False
for temp2 in Replies:#对回复进行分类
	Dfound = False
	if(temp2["author"]["user_name"] == ''):
		userTempo["id"] = temp2["author"]["portrait"]
		userTempo["author"] = "null"
	else:
		userTempo["author"] = temp2["author"]["user_name"]
	userTempo["postid"] = temp2["content"]["post_id"]
	userTempo["tid"] = temp2["content"]["thread_id"]
	bn = 0
	while bn < len(RPAuthors):
		if (RPAuthors[bn]["name"] == (userTempo["author"] if(userTempo["author"] !="null") else userTempo["id"])):
			RPAuthors[bn]["pids"].append(userTempo["postid"])
			RPAuthors[bn]["tids"].append(userTempo["tid"])
			Dfound=True
		bn=bn+1
	if(Dfound == False):
		RPAuthors[bn]={}
		RPAuthors[bn]['name'] = userTempo["author"] if(userTempo["author"]!="null") else userTempo["id"]
		RPAuthors[bn]["pids"] = list()
		RPAuthors[bn]["tids"] = list()
		RPAuthors[bn]["pids"].append(userTempo["postid"])
		RPAuthors[bn]["tids"].append(userTempo["tid"])
		RPAuthors[bn]["Weight"] = 0
	a=a+1

n=0
for temp in Replies:
	if (temp):
		Reply[n] = {}
		Reply[n]["tid"] = temp["content"]["thread_id"]
		Reply[n]["pid"] = temp["content"]["post_id"]
		if(temp["author"]["user_name"] != ''):
			Reply[n]["author"] = temp["author"]["user_name"]
		else:
			Reply[n]["author"] = "null"
			Reply[n]["id"] = temp["author"]["portrait"]
		Reply[n]["Weight"] = 0
		Reply[n]["Content"] = temp["content"]["content"]
		n = n + 1
	else:
		break
#STEP8////////////////////////////////////////////////////
print("执行Step8>>计算回复对象权值")
for tempx in Reply:#关键字过滤
	for tempz in BlackKeyWords:
		if(tempz in Reply[tempx]["Content"]):
			TOperate(6,[],TargetMember = Reply[tempx]["author"] if(Reply[tempx]["author"] != "null") else Reply[tempx]["id"],Weight = BlackKeyWords_Weight)
			TOperate(5,[Reply[tempx]["pid"]],Weight = BlackKeyWords_Weight)
	for tempm in WhiteKeyWords:
		if(tempm in Reply[tempx]["Content"]):
			TOperate(6,[],TargetMember = Reply[tempx]["author"] if(Reply[tempx]["author"] != "null") else Reply[tempx]["id"],Weight = WhiteKeyWords_MinusWeight)
			TOperate(5,[Reply[tempx]["pid"]],Weight = WhiteKeyWords_MinusWeight)
	if (len(Reply[tempx]["Content"]) < Reply_ContentLength_Limit):
			TOperate(6,[],TargetMember = Reply[tempx]["author"] if(Reply[tempx]["author"] != "null") else Reply[tempx]["id"],Weight = Tie_LimitWeight_per_item)
			TOperate(5,[Reply[tempx]["pid"]],Weight = Tie_LimitWeight_per_item)
pass
templist = []
for tempx in RPAuthors:#黑名单过滤
	if(Is_in_BlackList(RPAuthors[tempx]["name"])):
		bg = 0
		for tempa in RPAuthors[tempx]["pids"]:
			templist.append(str(tempa))
			bg=bg+1
		TOperate(2,templist,RPAuthors[tempx]["name"],"您在黑名单中，贴吧守护者已自动对您进行处理，如有异议请询问吧务",1)
		AddIntoRecList(RPAuthors[tempx]["name"],"999","检测到黑名单中记录",2)
		print("检测到黑名单中用户："+RPAuthors[tempx]["name"])
		print("清除其帖子：")
		print(templist)
		templist = []
pass
RequestFinned = False
Resss = []
for tempx in RPAuthors:#遍历用户
	RPAuthorDetailGet(tempx)
while(not RequestFinned):
	for i in RPAuthors:
		try:
			Resss.append(RPAuthors[i]["FansCount"])
		except:
			Resss.append(-2)
		try:
			Resss.append(RPAuthors[i]["HistoryTieCount"])
		except:
			Resss.append(-2)
		try:
			Resss.append(RPAuthors[i]["SubsCount"])
		except:
			Resss.append(-2)
	pass
	for a in Resss:
		if(a==-2):
			Resss = []
			RequestFinned = False
			break;
		else:
			RequestFinned = True
pass
for tempx in RPAuthors:
	if (RPAuthors[tempx]["HistoryTieCount"] < Member_historyTie_QuantityLimit):
		TOperate(6,[],RPAuthors[tempx]["name"],Weight = Member_LimitWeight_per_item)
		TOperate(5,RPAuthors[tempx]["pids"],Weight = Member_LimitWeight_per_item)
		pass;
	if (RPAuthors[tempx]["SubsCount"] < Member_Subs_Limit):
		TOperate(6,[],RPAuthors[tempx]["name"],Weight = Member_LimitWeight_per_item)
		TOperate(5,RPAuthors[tempx]["pids"],Weight = Member_LimitWeight_per_item)
		pass;
	if (RPAuthors[tempx]["FansCount"] < Member_Fans_Limit):
		TOperate(6,[],RPAuthors[tempx]["name"],Weight = Member_LimitWeight_per_item)
		TOperate(5,RPAuthors[tempx]["pids"],Weight = Member_LimitWeight_per_item)
		pass;
pass
#STEP-END/////////////////////////////////////////////////
print("执行Step-END>>总权值计算并进行最终处理")
'''
for tempx in Authors:
	if (Authors[tempx]["Weight"] >= Ban_Total and (not Is_in_WhiteList(Authors[tempx]["name"]))):
		TOperate(1,[],Authors[tempx]["name"],BanWeight = Authors[tempx]["Weight"])
		AddIntoRecList(Authors[tempx]["name"],str(Authors[tempx]["Weight"]),"违规综合权值达到封禁处理标准",0)
		print("封禁用户:"+Authors[tempx]["name"])

pass
'''
FinalAuthor = []
MGW = 0
BKL = False
for aaaa in Authors:
	for bbbb in RPAuthors:
		if (RPAuthors[bbbb]["name"] == Authors[aaaa]["name"]):
			MGW = RPAuthors[bbbb]["Weight"] + Authors[aaaa]["Weight"]
			FinalAuthor.append({"name":RPAuthors[bbbb]["name"],"Weight":MGW})
			RPAuthors[bbbb]["isF"] = True
			Authors[aaaa]["isF"] = True
			BKL = True
			break
	if(BKL):
		BKL = False
		continue
	FinalAuthor.append({"name":Authors[aaaa]["name"],"Weight":Authors[aaaa]["Weight"]})
	Authors[aaaa]["isF"] = True
pass
for aaaa in Authors:
	try:
		temp = Authors[aaaa]["isF"]
	except:
		temp = False
	if(not temp):
		FinalAuthor.append({"name":Authors[aaaa]["name"],"Weight":Authors[aaaa]["Weight"]})
pass
for bbbb in RPAuthors:
	try:
		temp = RPAuthors[bbbb]["isF"]
	except:
		temp = False
	if(not temp):
		FinalAuthor.append({"name":RPAuthors[bbbb]["name"],"Weight":RPAuthors[bbbb]["Weight"]})
pass

for tempx in FinalAuthor:
	if (tempx["Weight"] >= Ban_Total and (not Is_in_WhiteList(tempx["name"]))):
		TOperate(1,[],tempx["name"],BanWeight = tempx["Weight"])
		AddIntoRecList(tempx["name"],str(tempx["Weight"]),"违规综合权值达到封禁处理标准",0)
		print("封禁用户:"+tempx["name"])
pass

Deletetemp = list()
for tempx in Ties:
	if(Ties[tempx]["Weight"] >= DeleteTie_Total and (not Is_in_WhiteList(Ties[tempx]["author"] if(Ties[tempx]["author"] != "null") else Ties[tempx]["id"]))):
		Deletetemp.append(str(Ties[tempx]["tid"]))

pass
count = 0
class aaaaa:
	pass
coua = threading.active_count()
for tempx in Reply:
	if(Reply[tempx]["Weight"] >= DeleteTie_Total and (not Is_in_WhiteList(Reply[tempx]["author"] if(Reply[tempx]["author"] != "null") else Reply[tempx]["id"]))):
		obj = aaaaa()
		obj.tid = Reply[tempx]["tid"]
		obj.pid = Reply[tempx]["pid"]
		DeleteReply(obj)
		count = count + 1
pass
cou = threading.active_count()
while(not cou == coua):
	sleep(0.3)
	cou = threading.active_count()
pass
if(len(Deletetemp)):
	TOperate(0,Deletetemp)
	print("删除帖子：")
	print(Deletetemp)
print("共删除了 "+str(count)+" 条回复")
if(len(OperateTargetJSON)):
	for line in OperateTargetJSON:
		OperateTargetListStored.write(line+'\n')
	OperateTargetListStored.close()
	pass
print("~所有步骤执行完毕")
Pend = time.time()
print('运行耗时: %s Seconds'%(Pend-Pstart))
