#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
pulldata.py

#http://www.nus.edu.sg/cors/Reports/openbid_1A_20152016s2.html
#all mods are from here https://myaces.nus.edu.sg/cors/jsp/report/ModuleInfoListing.jsp

python pulldata 20152016s2

pulls statistics of all rounds from cors

"""
__author__ = "QuanYang"
__version__ = "0.1"

import os, sys, requests, re, json
from pprint import pprint

class CorsData:

	def __init__(self,semester):
		#	init variables
		self.semester = semester
		self.request = requests.session()
		self.all_Modules = dict()
		self.moduleSlots=dict()

		self.parseCorsSchedule()
		#	populate variables
		self.getAllModules()
		self.getAllOpenBidStats()
		self.getAllCloseBidStats()
		self.getAllBiddingSummary()

	def parseCorsSchedule(self):
		filename = "corsSchedule_%s.json"%self.semester
		schedule = file(filename,"rb")
		self.schedule = json.loads(schedule.read())

	def getAllModules(self):
		url = "https://myaces.nus.edu.sg/cors/jsp/report/ModuleInfoListing.jsp"
		r = self.request.get(url)
		if r.status_code == 200:
			data = r.text.strip().replace("  ","").replace("\r","").replace("\n","").replace("\t","")
			results = re.findall(r'valign="top">(.+?)<tr',data)[1:]

			self.modules = dict()
			for result in results:
				data_split = re.findall(r"<div [^>]+>(.+?)</div>",result)
				module_Code = data_split[1].split(">")[1].split("<")[0]
				module_Title = data_split[2]
				module_Session = data_split[4]
				self.modules[module_Code] = data_split[2:]

	def getOpenBid(self,round,buffer):
		url = "http://www.cors.nus.edu.sg/Reports/openbid_%s_%s.html"%(round,self.semester)
		r = self.request.get(url);
		if r.status_code == 200:
			data = r.text.strip().replace("  ",'').replace("\r\n","")
			results = re.findall(r'<tr valign=top bgcolor=\#[a-f0-9A-F]{6}>(.*?)</tr>',data)
			prevmod = "";
			for result in results:
				if "<td colspan=2>" in result:
					#belongs to prev mod
					data_split = re.findall(r'<td><p>(\d+?)</p></td>',result)
					buffer[prevmod] += int(data_split[0])
				else:
					data_split = result.replace("</p></td>","").split("<td><p>")[1:]
					key = (data_split[0],data_split[1])
					if key in buffer:
						buffer[key] += int(data_split[2])
					else:
						buffer[key] = int(data_split[2])
					prevmod = key

	def getCloseBid(self,round,buffer):
		closingTime = "1300"
		for data in self.schedule:
			if round == data['round']:
				# becomes 13:00:00
				closingTime = data['openBiddingEnd'][-8:].replace(":","")[0:4]

		url = "http://www.cors.nus.edu.sg/Reports/closebidinfo_%s_%s_%s.html"%(round,closingTime,self.semester)
		r = self.request.get(url)
		if r.status_code == 200:
			data = r.text.strip().replace("  ",'').replace("\r\n","").replace("\t","")
			results = re.findall(r'<tr valign=top bgcolor=\#[a-f0-9A-F]{6}>(.*?)</tr>',data)
			prevmod = "";
			for result in results:
				if "<td colspan=2>" in result:
					#belongs to prev mod
					data_split = re.findall(r'<td><p>(\d+?)</p></td>',result)
					buffer[prevmod] += int(data_split[1])
				else:
					data_split = result.replace("</p></td>","").split("<td><p>")[1:]
					key = (data_split[0],data_split[1])
					if key in buffer:
						buffer[key] += int(data_split[4])
					else:
						buffer[key] = int(data_split[4])
					prevmod = key

	def getSummary(self,round,buffer):
		url = "http://www.cors.nus.edu.sg/Reports/successbid_%s_%s.html"%(round,self.semester)
		r = self.request.get(url)
		if r.status_code == 200:
			data = r.text.strip().replace("  ",'').replace("\r\n","").replace("\t","")
			results = re.findall(r'<tr valign=top bgcolor=\#[a-f0-9A-F]{6}>(.*?)</tr>',data)
			prevmod = "";
			for result in results:
				if "<td colspan=2>" in result:
					#belongs to prev mod
					data_split = re.findall(r'<td><p>(\d+?)</p></td>',result)
					buffer[prevmod] += int(data_split[1])
				else:
					data_split = result.replace("</p></td>","").split("<td><p>")[1:]
					key = (data_split[0],data_split[1])
					if key in buffer:
						buffer[key] += int(data_split[3])
					else:
						buffer[key] = int(data_split[3])
					prevmod = key

	def getAllBiddingSummary(self):
		self.round1A_Summary = dict()
		self.getSummary("1A",self.round1A_Summary)
		self.round1B_Summary = dict()
		self.getSummary("1B",self.round1B_Summary)
		self.round2A_Summary = dict()
		self.getSummary("2A",self.round2A_Summary)
		self.round2B_Summary = dict()
		self.getSummary("2B",self.round2B_Summary)
		self.round3A_Summary = dict()
		self.getSummary("3A",self.round3A_Summary)
		self.round3B_Summary = dict()
		self.getSummary("3B",self.round3B_Summary)

	def getAllCloseBidStats(self):
		self.round1A_CloseBid = dict()
		self.getCloseBid("1A",self.round1A_CloseBid)
		self.round1B_CloseBid = dict()
		self.getCloseBid("1B",self.round1B_CloseBid)
		self.round2A_CloseBid = dict()
		self.getCloseBid("2A",self.round2A_CloseBid)
		self.round2B_CloseBid = dict()
		self.getCloseBid("2B",self.round2B_CloseBid)
		self.round3A_CloseBid = dict()
		self.getCloseBid("3A",self.round3A_CloseBid)
		self.round3B_CloseBid = dict()
		self.getCloseBid("3B",self.round3B_CloseBid)

	def getAllOpenBidStats(self):
		self.round1A_OpenBid = dict()
		self.getOpenBid("1A",self.round1A_OpenBid)
		self.round1B_OpenBid = dict()
		self.getOpenBid("1B",self.round1B_OpenBid)
		self.round2A_OpenBid = dict()
		self.getOpenBid("2A",self.round2A_OpenBid)
		self.round2B_OpenBid = dict()
		self.getOpenBid("2B",self.round2B_OpenBid)
		self.round3A_OpenBid = dict()
		self.getOpenBid("3A",self.round3A_OpenBid)
		self.round3B_OpenBid = dict()
		self.getOpenBid("3B",self.round3B_OpenBid)

		#assuming self.round 1b - self.round 1a would be new mods not in self.round 1a, and so forth
		self.round1A_Mods = set(self.round1A_OpenBid.keys())
		self.round1B_Mods = set(self.round1B_OpenBid.keys())
		self.round2A_Mods = set(self.round2A_OpenBid.keys())
		self.round2B_Mods = set(self.round2B_OpenBid.keys())
		self.round3A_Mods = set(self.round3A_OpenBid.keys())
		self.round3B_Mods = set(self.round3B_OpenBid.keys())

		for key in self.round1A_Mods:
			self.moduleSlots[key] = (self.round1A_OpenBid[key],"1A")
		for key in self.round1B_Mods-set(self.moduleSlots.keys()):
			self.moduleSlots[key] = (self.round1B_OpenBid[key],"1B")
		for key in self.round2A_Mods-set(self.moduleSlots.keys()):
			self.moduleSlots[key] = (self.round2A_OpenBid[key],"2A")
		for key in self.round2B_Mods-set(self.moduleSlots.keys()):
			self.moduleSlots[key] = (self.round2B_OpenBid[key],"2B")
		for key in self.round3A_Mods-set(self.moduleSlots.keys()):
			self.moduleSlots[key] = (self.round3A_OpenBid[key],"3A")
		for key in self.round3B_Mods-set(self.moduleSlots.keys()):
			self.moduleSlots[key] = (self.round3B_OpenBid[key],"3B")

	def checkLatestRound(self):
		rounds = ["3B","3A","2B","2A","1B","1A"]
		for round in rounds:
			if getattr(self,'round%s_OpenBid'%round):
				return round

	def findModule(self, module = ("ACC1002","LECTURE V01")):
		self.latestRound = self.checkLatestRound()

		if module in self.moduleSlots:
			moduleData = self.moduleSlots[module]
			numOfBidders = getattr(self,'round%s_CloseBid'%moduleData[1])[module]
			numOfBidders_Summary = getattr(self,'round%s_Summary'%moduleData[1])[module]
			if numOfBidders_Summary > numOfBidders:
				numOfBidders = numOfBidders_Summary
			print "Module %s @ %s has %d slots."%(module[0],module[1],moduleData[0])
			print "Number of bidders: %d"%numOfBidders
			ratio = float(numOfBidders)/float(moduleData[0])
			print "Ratio: %.2f"%ratio
			if ratio<0.9:
				print "Healthy, need not rush to bid, would have plenty in round 3."
			else:
				print "Unhealthy, bid as much as you can afford."
		else:
			print "Module not found!"

def main():
	semester = sys.argv[1]
	cors = CorsData(semester)
	cors.findModule((sys.argv[2],sys.argv[3]))

if __name__ == '__main__':
	main()