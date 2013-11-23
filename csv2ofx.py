#!/usr/bin/env python
# coding: utf-8

from xml.dom.minidom import Document, Text, parseString
import copy
import csv
import time
import codecs
from transliterate.utils import translit
from odict import odict

from logic import Converter, Node

def dict2xml(data, *args, **kwargs):
		return Converter(*args, **kwargs).build(data)

dates=[]

class Transaction:
		tid = 0
		def __init__(self, debcred, ttype, posted, avail, amount, name):
				Transaction.inctid()
				dates.append(time.strptime(posted, "%d.%m.%Y %H:%M:%S"))
				self.ddict = odict((
						("TRNTYPE", debcred.upper()),
						("DTPOSTED" , time.strftime("%Y%m%d%H%M%S", time.strptime(posted, "%d.%m.%Y %H:%M:%S"))),
						("DTAVAIL" , time.strftime("%Y%m%d%H%M%S", time.strptime(avail, "%d.%m.%Y %H:%M:%S"))),
						("TRNAMT" , amount),
						("FITID" , self.tid),
						("NAME" , name),
						("MEMO" , ttype),
						))

		@classmethod
		def inctid(cls):
				cls.tid+=1


def csv_to_transaction(filepath):
		ret = []
		with open(filepath) as csvfile:
				reader = csv.reader(csvfile, delimiter=";")
				for e in reader:
						if e[2] == 'Debit':
								amount=unicode(-float(e[6]))
						else:
								amount=unicode(e[6])
						ret.append(Transaction(e[2],e[8].decode('cp1251'),e[0],e[1], amount, e[9].decode('cp1251')))
		dates.sort()


		return odict({
						"OFX":odict((
								("SIGNONMSGSRSV1", odict({
										"SONRS": odict((
												("STATUS" , odict((
														("CODE" , 0),
														("SEVERITY" , "INFO"),
												))),
												("DTSERVER", time.strftime("%Y%m%d%H%M%S", dates[-1])),
												("LANGUAGE", "RUS"),
										)),
								})),
								("BANKMSGSRSV1",odict({
										"TMTTRNRS":odict((
												("TRNUID", "0"),
												("STATUS", odict((
														("CODE" , 0),
														("SEVERITY" , "INFO"),
												))),
												("STMTRS", odict((
														("CURDEF", "RUR"),
														("BANKACCTFROM", odict((
																("BANKID", "TINKOFF"),
																("ACCTID", "0"),
																("ACCTTYPE", "CHECKING"),
														))),
														("BANKTRANLIST", odict((
																("DTSTART", time.strftime("%Y%m%d%H%M%S", dates[0])),
																("DTEND", time.strftime("%Y%m%d%H%M%S", dates[-1])),
																("STMTTRN", [ e.ddict for e in ret ]),
														))),
														("LEDGERBAL" , odict((
																("BALAMT", "0"),
																("DTASOF", time.strftime("%Y%m%d%H%M%S", dates[-1])),
														)))
												)))
										))
								}))
						))
				})


if __name__ == '__main__':

		
		xml = dict2xml(csv_to_transaction("ops.csv"))
		f = codecs.open("/Users/dindin/Dropbox/latest.ofx", encoding="utf-8", mode="w+")
		f.write("""<?xml version="1.0" encoding="utf-8"?>
<?OFX OFXHEADER="200" VERSION="211" SECURITY="NONE" OLDFILEUID="NONE" NEWFILEUID="NONE"?>
""")
		f.write(xml)
		f.close()
