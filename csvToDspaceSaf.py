''' csv convert to DSpace SAF format

Please see README.md in the same directory.

@Author TAI, CHUN-MIN <taichunmin@gmail.com>
'''

''' Default Settings '''
setting = {
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

import json, csv, sys, re, os, traceback, shutil, os.path as path, xml.etree.ElementTree as ET

# Remove last comma after inner json object
def jsonDelTrailingComma( json_str ):
	ret = []
	commaPos = inQuote = 0
	quoteSign = ''
	for i in json_str:
		if inQuote == 0:
			if i == '"' or i == "'":
				inQuote, quoteSign = 1, i
			elif i == ',':
				commaPos = 1
			elif (i == '}' or i == ']') and commaPos > 0:
				del(ret[-commaPos])

			# 在此計算 comma 的位置
			if i in " \f\n\r\t\v":
				commaPos += 1
			elif i != ',':
				commaPos = 0
		elif inQuote == 1:
			if i == '\\':
				inQuote = 2
			elif i == quoteSign:
				inQuote = 0
		else:
			inQuote = 1
		ret.append(i);
	return ''.join(ret)

# make directory recursively
def mkdir( dirpath ):
	if not path.isdir( dirpath ):
		os.makedirs( dirpath )
	return dirpath

# a auto-imcrement counter
def next_pki():
    next_pki.pki += 1
    return str(next_pki.pki)
next_pki.pki = 0

reDcname = re.compile( setting["dcNamePattern"] )
reHandle = re.compile( r"^\d+/\d+$" )

class InvalidCSVError(Exception): pass

def load_setting():
	try:
		with open('setting.json', encoding='utf8') as setting_json:
			setting.update( json.loads( jsonDelTrailingComma( setting_json.read() ) ) )
		# print( json.dumps(setting, sort_keys=True, indent=2) )
		return True
	except IOError as e:
		print("Can't read setting.json, use default setting.")
	except Exception as e:
		print( traceback.format_exc() )
	return False

def csv_dialect( fh ):
	fh.seek(0)
	dialect = csv.Sniffer().sniff( fh.read(1024) )
	fh.seek(0)
	return dialect

def main( csv_list ):
	ErrCnt = 0
	load_setting()
	if isinstance( csv_list, str ):
		csv_list = [csv_list,]
	for csvfname in csv_list:
		try:
			fnameMaj, fnameExt = path.splitext( path.basename( csvfname ))
			if not path.isfile(csvfname) or fnameExt.lower() != '.csv':
				raise InvalidCSVError( csvfname )
			with open( csvfname, newline='', encoding='utf8' ) as csvfh:
				csvBaseDir = path.dirname( path.abspath(csvfname) )
				safBaseDir = path.join( csvBaseDir, (fnameMaj or ('SAF' + next_pki())) )
				while path.isdir( safBaseDir ):
					safBaseDir = path.join( csvBaseDir, 'SAF'+next_pki() )
				else:
					mkdir( safBaseDir )

				for row in csv.DictReader(csvfh, dialect=csv_dialect(csvfh)):
					if not row.get( setting['fieldNameID'] ,''):
						itemDir = mkdir( path.join( safBaseDir, row[ setting['fieldNameID'] ] ))
					else:
						itemDir = mkdir( path.join( safBaseDir, 'item'+next_pki() ))
					dcXmlRoot = ET.fromstring('<?xml version="1.0" encoding="utf-8" standalone="no"?><dublin_core schema="dc"></dublin_core>')
					for k, v in row.items():
						matchDcname = reDcname.match( k )
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
						elif k == setting['fieldNameHandle'] and reHandle.match(v):
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
	if len(sys.argv)<2:
		# need to implement help block
		sys.exit(1)
	ErrCnt = main( sys.argv[1:] )
	if ErrCnt:
		input()
