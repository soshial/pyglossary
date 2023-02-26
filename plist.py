import json
import plistlib

import biplist

from pyglossary import Glossary
from pyglossary.plugins.appledict_bin import Reader
from pyglossary.plugins.appledict_bin.appledict_print import print_buffer_range


def plist_to_json_file(plist_file_path,json_file_path):
	with open(json_file_path, 'w') as f1:
		made_json = get_json_from_plist(plist_file_path)
		f1.write(json.dumps(made_json, sort_keys=True, indent=4, ensure_ascii=False))


def get_json_from_plist(filename: str):
	try:
		plist = biplist.readPlist(filename)
		return plist
	# print(json.dumps(plist)) #.replace('\'', '\"')
	except (biplist.InvalidPlistException, biplist.NotBinaryPlistException):
		print("Not a plist:")
		return plistlib.loads(open(filename, 'rb').read())


def parse_keytext(name, subfolder):
	print(name)
	glos = Glossary()
	reader = Reader(glos)
	metadata = reader.parseMetadata(
		f'/Users/soshial/Desktop/test_ready/{name}.dictionary/Contents/Info.plist')
	reader.setMetadata(metadata)
	key_text_data = reader.getKeyTextDataFromFile(
		f'/Users/soshial/Desktop/test_ready/{name}.dictionary/Contents/{subfolder}KeyText.data',
		reader._properties)
	with open(f"./expected_KeyText.data_{name}.txt", 'w') as fid:
		for article_address in sorted(key_text_data.keys()):
			fid.write(f'{article_address}\t{key_text_data[article_address]}\n')


if __name__ == "__main__":
	v = '10.5'
	for c in range(2):
		for t in range(1):
			name = f'006-en-oxfjord_v{v}_c{c}_t{t}'
			parse_keytext(name, '')
	v = '10.6'
	for c in range(0, 3):
		for t in range(0, 4):
			name = f'006-en-oxfjord_v{v}_c{c}_t{t}'
			parse_keytext(name, '')
	v = '10.11'
	name = f'006-en-oxfjord_v{v}_c{2}_t{3}'
	parse_keytext(name, 'Resources/')




	# for c in range(3):
	# 	for t in range(4):
	# 		name = f'006-en-oxfjord_v{v}_c{c}_t{t}'
	# 		plist_to_json_file(f"/Users/soshial/Desktop/pyglossary_apple_tests/{name}.dictionary/Contents/Info.plist", f'infoplist_{name}.json')

