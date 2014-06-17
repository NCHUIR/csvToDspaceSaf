import json, csv, sys, re, os, traceback, shutil, os.path as path, xml.etree.ElementTree as ET


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

def mkdir( dirpath ):
	if not path.isdir( dirpath ):
		os.makedirs( dirpath )
	return dirpath

def next_pki():
    next_pki.pki += 1
    return str(next_pki.pki)
next_pki.pki = 0

''' Default Settings '''
setting = {
	'delimiter': ',',
	'quotchar': '"',
	'dataDelimiter': '||', # This is to delimiter data in multi-field
	"ignoreField":[
	],
	"multiField":[
		'dc.contributor',
		'dc.contributor.advisor',
		'dc.contributor.author',
		'dc.contributor.editor',
		'dc.contributor.illustrator',
		'dc.contributor.other',
		'dc.contributor.cataloger',
		'dc.creator',
		'dc.subject',
		'dc.subject.classification',
		'dc.subject.ddc',
		'dc.subject.lcc',
		'dc.subject.lcsh',
		'dc.subject.mesh',
		'dc.subject.other',
	],
}
''' End of Default Settings '''

try:
	with open('setting.json', encoding='utf8') as setting_json:
		setting.update( json.loads( jsonDelTrailingComma( setting_json.read() ) ) )
except IOError as e:
	print("Can't read setting.json, use default setting")
except Exception as e:
	print( traceback.format_exc() )

# print( json.dumps(setting, sort_keys=True, indent=2) )

if len(sys.argv)<2:
	# need to implement help block
	sys.exit(1)
try:
	reDcname = re.compile( r"^dc\.(\w+)(?:\.(\w+))?(?:\[(\w+)\])?$" )
	reHandle = re.compile( r"^\d+/\d+^" )
	for csvfname in sys.argv[1:]:
		with open( csvfname, 'r', encoding='utf8' ) as csvfh:
			fnameMaj, fnameExt = path.splitext( path.basename( csvfname ))
			csvBaseDir = path.dirname( path.abspath(csvfname) )

			safBaseDir = path.join( csvBaseDir, (fnameMaj or ('SAF' + next_pki())) )
			while path.isdir( safBaseDir ):
				safBaseDir = path.join( csvBaseDir, 'SAF'+next_pki() )
			else:
				mkdir( safBaseDir )

			for row in csv.DictReader(csvfh):
				if not row['id']:
					itemDir = mkdir( path.join( safBaseDir, row['id'] ))
				else:
					itemDir = mkdir( path.join( safBaseDir, 'item'+next_pki() ))
				dcXmlRoot = ET.fromstring('<?xml version="1.0" encoding="utf-8" standalone="no"?><dublin_core schema="dc"></dublin_core>')
				for k, v in row.items():
					matchDcname = reDcname.match( k )
					if matchDcname is not None:
						xmldatas = []
						dcname = '.'.join(filter(bool, ['dc',matchDcname.group(1),matchDcname.group(2)] ))
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
					elif k == 'handle' and reHandle.match(v):
						with open( path.join( itemDir, 'handle' ), 'w', encoding='utf8') as itemHandleFh:
							print( v, file=itemHandleFh )
					elif k == 'contents' and v:
						with open( path.join( itemDir, 'contents' ), 'w', encoding='utf8') as itemContentsFh:
							for i in v.split( setting['dataDelimiter'] ):
								bitstreamPath = path.join(csvBaseDir,i)
								if path.isfile( bitstreamPath ) and shutil.copy2( bitstreamPath, itemDir ):
									print( i, file=itemContentsFh )
				ET.ElementTree(dcXmlRoot).write(path.join( itemDir, 'dublin_core.xml' ), encoding='utf-8')
except Exception as e:
	print( traceback.format_exc() )
