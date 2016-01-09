#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
pulldata.py

#http://www.nus.edu.sg/cors/Reports/openbid_1A_20152016s2.html
#all mods are from here https://myaces.nus.edu.sg/cors/jsp/report/ModuleInfoListing.jsp

python pulldata 20152016s2

pulls data of all rounds from cors

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

		self.parseCorsSchedule()
		
		#	populate variables
		self.getAllOpenBidStats()
		self.getAllCloseBidStats()
		self.getAllBiddingSummary()
		self.getAllModules()


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
					buffer[prevmod][0] += int(data_split[1])
					buffer[prevmod][1] += int(data_split[2])
				else:
					data_split = result.replace("</p></td>","").split("<td><p>")[1:]
					key = (data_split[0],data_split[1])
					if key in buffer:
						buffer[key][0] += int(data_split[4])
						buffer[key][1] += int(data_split[5])
					else:
						buffer[key] = [int(data_split[4]),int(data_split[5])]
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
		round1A_Summary = dict()
		self.getSummary("1A",round1A_Summary)
		round1B_Summary = dict()
		self.getSummary("1B",round1B_Summary)
		round2A_Summary = dict()
		self.getSummary("2A",round2A_Summary)
		round2B_Summary = dict()
		self.getSummary("2B",round2B_Summary)
		round3A_Summary = dict()
		self.getSummary("3A",round3A_Summary)
		round3B_Summary = dict()
		self.getSummary("3B",round3B_Summary)


	def getAllCloseBidStats(self):
		round1A_CloseBid = dict()
		self.getCloseBid("1A",round1A_CloseBid)
		round1B_CloseBid = dict()
		self.getCloseBid("1B",round1B_CloseBid)
		round2A_CloseBid = dict()
		self.getCloseBid("2A",round2A_CloseBid)
		round2B_CloseBid = dict()
		self.getCloseBid("2B",round2B_CloseBid)
		round3A_CloseBid = dict()
		self.getCloseBid("3A",round3A_CloseBid)
		round3B_CloseBid = dict()
		self.getCloseBid("3B",round3B_CloseBid)

	def getAllOpenBidStats(self):
		round1A_OpenBid = dict()
		self.getOpenBid("1A",round1A_OpenBid)
		round1B_OpenBid = dict()
		self.getOpenBid("1B",round1B_OpenBid)
		round2A_OpenBid = dict()
		self.getOpenBid("2A",round2A_OpenBid)
		round2B_OpenBid = dict()
		self.getOpenBid("2B",round2B_OpenBid)
		round3A_OpenBid = dict()
		self.getOpenBid("3A",round3A_OpenBid)
		round3B_OpenBid = dict()
		self.getOpenBid("3B",round3B_OpenBid)

		#assuming round 1b - round 1a would be new mods not in round 1a, and so forth
		round1B_Mods = set(round1B_OpenBid.keys())
		round2A_Mods = set(round2A_OpenBid.keys())
		round2B_Mods = set(round2B_OpenBid.keys())
		round3A_Mods = set(round3A_OpenBid.keys())
		round3B_Mods = set(round3B_OpenBid.keys())

		self.moduleSlots = round1A_OpenBid
		for key in round1B_Mods-set(self.moduleSlots.keys()):
			self.moduleSlots[key] = round1B_OpenBid[key]
		for key in round2A_Mods-set(self.moduleSlots.keys()):
			self.moduleSlots[key] = round2A_OpenBid[key]
		for key in round2B_Mods-set(self.moduleSlots.keys()):
			self.moduleSlots[key] = round2B_OpenBid[key]
		for key in round3A_Mods-set(self.moduleSlots.keys()):
			self.moduleSlots[key] = round3A_OpenBid[key]
		for key in round3B_Mods-set(self.moduleSlots.keys()):
			self.moduleSlots[key] = round3B_OpenBid[key]

		
def main():
	semester = sys.argv[1]
	cors = CorsData(semester)


if __name__ == '__main__':
	main()