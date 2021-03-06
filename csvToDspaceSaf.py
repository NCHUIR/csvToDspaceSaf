''' csv convert to DSpace SAF format

Please see README.md in the same directory.

@Author TAI, CHUN-MIN <taichunmin@gmail.com>
'''

import json, csv, sys, re, os, traceback, shutil, os.path as path, xml.etree.ElementTree as ET

class csvToDspaceSaf:

	def __init__(self,input_setting = False):

		''' Default Settings '''
		self.setting = {
			"dataDelimiter": "||", # This is to delimiter data in multi-field
			"fieldNameID": "id",
			"fieldNameHandle": "handle",
			"fieldNameContents": "contents",
			"ignoreField":[
				"dc.date.accessioned",
				"dc.date.available",
				"dc.date.issued",
				"dc.identifier.uri",
				"dc.description.provenance",
			],
			"multiField":[
				"dc.contributor",
				"dc.contributor.advisor",
				"dc.contributor.author",
				"dc.contributor.editor",
				"dc.contributor.illustrator",
				"dc.contributor.other",
				"dc.contributor.cataloger",
				"dc.creator",
				"dc.subject",
				"dc.subject.classification",
				"dc.subject.ddc",
				"dc.subject.lcc",
				"dc.subject.lcsh",
				"dc.subject.mesh",
				"dc.subject.other",
				"dc.subject[zh_TW]",
				"dc.subject[en_US]"
			],
			"dcNamePattern": "^dc\.(\w+)(?:\.(\w+))?(?:\[(\w+)\])?$", # should match {1:'element', 2:'qualifier', 3:'langISO'}
		}
		''' End of Default Settings '''

		if input_setting:
			self.setting.update(input_setting)

		self.reDcname = re.compile( self.setting["dcNamePattern"] )
		self.reHandle = re.compile( r"^\d+/\d+$" )

	@staticmethod
	def previusDir(dirpath): # get previous directive,ex: /var/www => /var/
		return os.path.abspath(os.path.join(dirpath, os.pardir))

	@staticmethod
	def mkSeqDir(dirpath): # Make Sequence Directives
		dirDeli = "_"
		fPrefix = os.path.basename(dirpath) + dirDeli
		result = dirpath + dirDeli + "0"
		if path.exists(result):
			result = dirpath + dirDeli + str(
				max(
					[int(f.split(dirDeli)[-1]) for f in os.listdir(__class__.previusDir(dirpath)) if fPrefix in f]
				) + 1
			)
		os.makedirs(result)
		return result

	@staticmethod
	def mkNoColiDir(dirpath): # Make No Colision Directives
		if path.exists(dirpath):
			return __class__.mkSeqDir(dirpath)
		else:
			os.makedirs(dirpath)
			return dirpath

	@staticmethod
	def csv_dialect( fh ):
		fh.seek(0)
		dialect = csv.Sniffer().sniff( fh.read(4096) )
		dialect.skipinitialspace=True
		fh.seek(0)
		return dialect

	def main( self,csv_list,output_folder ):
		Err = []
		ch2replace = ["‘","’","“","”","\"\"","''"]										#replace the spacial symbols:"‘","’","“","”","\"\"" with "'"
		setting = self.setting
		if isinstance( csv_list, str ):
			csv_list = [csv_list,]
		print("Start to process...")
		for csvfname in csv_list:
			try:
				fnameMaj, fnameExt = path.splitext( path.basename( csvfname ))
				if not path.isfile(csvfname) or fnameExt.lower() != '.csv':
					raise Exception("[%s] not Exists or not a csv file!" % csvfname)
				newCsvfname = os.path.abspath(os.path.join(__class__.previusDir(csvfname),"New"+path.basename( csvfname )))	
				with open( csvfname,'r', newline='', encoding='utf8' ) as csvfr:					
					with open( newCsvfname,'w', newline='', encoding='utf8' ) as csvfw:
						for content in csvfr:
							content=content.replace(",\"\"\"",",\"'")
							content=content.replace("\"\"\",","'\",")
							content=content.replace("。'","，'")
							for ch in ch2replace:
								content=content.replace(ch,"'")
							csvfw.write(content)
				with open( newCsvfname, newline='', encoding='utf8' ) as csvfh:
					csvBaseDir = __class__.previusDir(newCsvfname)
					safBaseDir = __class__.mkNoColiDir( path.join( output_folder, path.basename(csvBaseDir) ) )
					print("Processing [%s] => [%s]" % (newCsvfname,safBaseDir))
					try:
						csvObj = csv.DictReader(csvfh, dialect=__class__.csv_dialect(csvfh),skipinitialspace=True)
						'''count = 0
						for row in csvObj:
							count = count + 1
							for k, v in row.items():
								if count < 4 :
									print(k)
									print(v)'''
					except Exception as e:
						print("dialect sniff Error, using default fallback...")
						csvfh.seek(0)
						csvObj = csv.DictReader(csvfh)
					for row in csvObj:
						if row.get( setting['fieldNameID'] ,False):
							itemDir = __class__.mkNoColiDir( path.join( safBaseDir, row[ setting['fieldNameID'] ] ) )
						else:
							itemDir = __class__.mkSeqDir( path.join( safBaseDir, 'item' ) )
						print("\tProcessing [%s]..." % (itemDir))
						dcXmlRoot = ET.fromstring('<?xml version="1.0" encoding="utf-8" standalone="no"?><dublin_core schema="dc"></dublin_core>')
						for k, v in row.items():
							if k is not None:
								k=k.strip()
							matchDcname = self.reDcname.match( k )
							if matchDcname is not None:
								xmldatas = []
								dcname = '.'.join( filter( bool, ['dc',matchDcname.group(1),matchDcname.group(2)] ) )
								if dcname in setting['ignoreField']:
									continue
								elif dcname in setting['multiField']:
									xmldatas += [ i.strip() for i in v.split( setting['dataDelimiter'] ) ]
								else:
									xmldatas += [ v.strip(), ]
								for xmldata in filter(bool, xmldatas):
									dcDom = ET.SubElement( dcXmlRoot, 'dcvalue' )
									dcDom.text = xmldata
									dcDom.attrib['element'] = matchDcname.group(1)
									dcDom.attrib['qualifier'] = ( matchDcname.group(2) or 'none' )
									if matchDcname.group(3):
										dcDom.attrib['language'] = matchDcname.group(3)
							elif k == setting['fieldNameHandle'] and self.reHandle.match(v):
								with open( path.join( itemDir, 'handle' ), 'w', encoding='utf8') as itemHandleFh:
									print( v, file=itemHandleFh )
							elif k == setting['fieldNameContents'] and v:
								with open( path.join( itemDir, 'contents' ), 'w', encoding='utf8') as itemContentsFh:
									for i in v.split( setting['dataDelimiter'] ):
										bitstreamPath = path.join(csvBaseDir,i)
										if path.isfile( bitstreamPath ) and shutil.copy2( bitstreamPath, itemDir ):
											print( i, file=itemContentsFh )
						ET.ElementTree(dcXmlRoot).write(path.join( itemDir, 'dublin_core.xml' ), encoding='utf-8')
			except Exception as e:
				print( type(e), ':', e.args )
				print( traceback.format_exc() )
				Err.append(e)
			else:
				print("Process Completed!")
			os.remove(csvfname)																				#remove original csv
			os.rename(newCsvfname,csvfname)																	#rename new csv to original name
		return Err

if __name__ == "__main__":
	if len(sys.argv)<3:
		print("Usage:\n\tpython3 "+sys.argv[0]+" <csv1> [<csv2>[<csv3> ...]] <output_folder>")
		sys.exit(1)
	main = csvToDspaceSaf()
	ErrCnt =main.main( sys.argv[1:-1],sys.argv[-1] )
	if ErrCnt:
		input()
