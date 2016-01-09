#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
pulldata.py

#http://www.nus.edu.sg/cors/Reports/openbid_1A_20152016s2.html

python pulldata 20152016s2

pulls data of all rounds from cors

"""
__author__ = "QuanYang"
__version__ = "0.1"

import os, sys, requests,re

def getOpenBid(request,semester,round,type,buffer):
	url = "http://www.cors.nus.edu.sg/Reports/%s_%s_%s.html"%(type,round,semester)
	out = request.get(url);
	data = out.text.strip().replace("  ",'').replace("\r\n","")
	
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

def main():
	semester = sys.argv[1]
	request = requests.session()

	round1A_openbid = dict()
	getOpenBid(request,semester,"1A","openbid",round1A_openbid)

	roudn1B_openbid = dict()

	round2A_openbid = dict()
	getOpenBid(request,semester,"2A","openbid",round2A_openbid)

	round2B_openbid = dict()
	getOpenBid(request,semester,"2B","openbid",round2B_openbid)



if __name__ == '__main__':
	main()