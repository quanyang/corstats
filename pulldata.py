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

import os, sys, requests,re

class CorsData:

	def __init__(self,semester):
		#	init variables
		self.semester = semester
		self.request = requests.session()
		self.all_Modules = dict()


		#	populate variables
		#self.getAllOpenBid()
		self.getAllModules()

	def getAllModules(self):
		url = "https://myaces.nus.edu.sg/cors/jsp/report/ModuleInfoListing.jsp"
		r = self.request.get(url)
		print r.text.strip().replace("  ","").replace("\r\n","").replace("\t","")

	def getOpenBid(self,round,buffer):
		url = "http://www.cors.nus.edu.sg/Reports/%s_%s_%s.html"%("openbid",round,self.semester)
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

	def getAllOpenBid(self):
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

		#assuming round 1b - round 1a would be new mods not in round 1a, and so forth
		self.round1A_Mods = set(self.round1A_OpenBid.keys())
		self.round1B_Mods = set(self.round1B_OpenBid.keys())
		self.round2A_Mods = set(self.round2A_OpenBid.keys())
		self.round2B_Mods = set(self.round2B_OpenBid.keys())
		self.round3A_Mods = set(self.round3A_OpenBid.keys())
		self.round3B_Mods = set(self.round3B_OpenBid.keys())
		
def main():
	semester = sys.argv[1]
	cors = CorsData(semester)


if __name__ == '__main__':
	main()