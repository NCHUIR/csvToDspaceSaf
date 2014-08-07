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
			],
			"dcNamePattern": "^dc\\.(\\w+)(?:\\.(\\w+))?(?:\\[(\\w+)\\])?$", # should match {1:'element', 2:'qualifier', 3:'langISO'}
		}
		''' End of Default Settings '''

		if input_setting:
			self.setting.update(input_setting)

		self.reDcname = re.compile( self.setting["dcNamePattern"] )
		self.reHandle = re.compile( r"^\d+/\d+$" )

	class InvalidCSVError(Exception): pass

	def previusDir(dirpath): # get previous directive,ex: /var/www => /var/
		return os.path.abspath(os.path.join(dirpath, os.pardir))

	def mkSeqDir(dirpath): # Make Sequence Directives
		dirDeli = "_"
		fPrefix = os.path.basename(dirpath) + dirDeli
		result = dirpath + dirDeli + "0"
		if path.exists(result):
			result = dirpath + dirDeli + str(
				max(
					[int(f.split(dirDeli)[-1]) for f in os.listdir(csvToDspaceSaf.previusDir(dirpath)) if fPrefix in f]
				) + 1
			)
		os.makedirs(result)
		return result

	def mkNoColiDir(dirpath): # Make No Colision Directives
		if path.exists(dirpath):
			return csvToDspaceSaf.mkSeqDir(dirpath)
		else:
			os.makedirs(dirpath)
			return dirpath

	def csv_dialect( fh ):
		fh.seek(0)
		dialect = csv.Sniffer().sniff( fh.read(1024) )
		fh.seek(0)
		return dialect

	def main( self,csv_list,output_folder ):
		ErrCnt = 0
		setting = self.setting
		if isinstance( csv_list, str ):
			csv_list = [csv_list,]
		for csvfname in csv_list:
			try:
				fnameMaj, fnameExt = path.splitext( path.basename( csvfname ))
				if not path.isfile(csvfname) or fnameExt.lower() != '.csv':
					raise InvalidCSVError( csvfname )
				with open( csvfname, newline='', encoding='utf8' ) as csvfh:
					csvBaseDir = csvToDspaceSaf.previusDir(csvfname)
					safBaseDir = csvToDspaceSaf.mkNoColiDir( path.join( output_folder, path.basename(csvBaseDir) ) )
					for row in csv.DictReader(csvfh, dialect=csvToDspaceSaf.csv_dialect(csvfh)):
						if row.get( setting['fieldNameID'] ,False):
							itemDir = csvToDspaceSaf.mkNoColiDir( path.join( safBaseDir, row[ setting['fieldNameID'] ] ) )
						else:
							itemDir = csvToDspaceSaf.mkSeqDir( path.join( safBaseDir, 'item' ) )
						dcXmlRoot = ET.fromstring('<?xml version="1.0" encoding="utf-8" standalone="no"?><dublin_core schema="dc"></dublin_core>')
						for k, v in row.items():
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
				ErrCnt+=1
		return ErrCnt

if __name__ == "__main__":
	if len(sys.argv)<3:
		print("Usage:\n\tpython3 "+sys.argv[0]+" <csv1> [<csv2>[<csv3> ...]] <output_folder>")
		sys.exit(1)
	main = csvToDspaceSaf()
	ErrCnt =main.main( sys.argv[1:-1],sys.argv[-1] )
	if ErrCnt:
		input()
