import re


def process_tilda(newline: str, all_keys_file) -> str:
	newline = newline.replace('<opt>', '').replace('</opt>', '')  # TODO process <opt>
	if newline.startswith('<ar>'):
		matches = re.match(r'<ar>(<k>.+</k>)<def>(.+)</def></ar>\n', newline)
		if matches is None:
			return newline
		else:
			key_section = matches.groups()[0]  # '<k>wyda|wać, <u>wydaję</u>, <u>wydaje</u></k><k>wyyyyyd</k>'
			all_keys = re.findall('<k>(.+?)</k>', key_section)  # ['wyda|wać, ~ję, ~je', 'wyyyyyd']
			root_def = matches.groups()[1]
			if len(all_keys) > 1:
				print('all_keys', all_keys)
			new_key_section = ''
			for key in all_keys:
				# @key - original key from xdxf: "wyda|wać, ~ję, ~je", "ciągn|ąć się"
				if '|' in key or ',' in key:  # cleaning dictionary keys from powszechny
					root_def = f'<gr><i>{key.replace("|", "")}</i></gr>' + root_def  # TODO <i> inside <gr> is removed ?!
					# @head_key - cleaned head of article: "abat", "ciągnąć się"
					if key.find(',') != -1:
						head_key = key[:key.find(',')].replace('|', '')
					else:
						head_key = key.replace('|', '')
					# 'ciągn|ąć'
					if key.find('|') != -1:
						if head_key.find(' ') != -1:
							key_stem = key[:key.find('|')]  # 'ciągn'
							key_full = head_key[:head_key.find(' ')]  # 'ciągnąć'
						else:
							key_stem = key[:key.find('|')]
							key_full = head_key
					else:
						if head_key.find(' ') != -1:
							key_stem = head_key[:head_key.find(' ')]
							key_full = head_key[:head_key.find(' ')]
						else:
							key_stem = head_key
							key_full = head_key
				else:
					head_key = key
					key_stem = head_key
					key_full = head_key
				if '~' in newline:
					# <ex> <b>odzyskać ~</b> прийти́ в себя́, очну́ться;</ex>
					# <ex> <b>odzyskać <mrkd>świadomość</mrkd></b> прийти́ в себя́, очну́ться;</ex>

					root_def = re.sub(r'<ex>([^<]*)<b>([^<]+)~(\w+)([^<]*)</b>',
									  r'<ex>\g<1><ex_orig>\g<2><mrkd>' +
									  key_stem +
									  r'\g<3></mrkd>\g<4></ex_orig>',
									  root_def)
					root_def = re.sub(r'~(\w+)',
									  # '<u>' +
									  key_stem + '\g<1>'
									  # '</u>'
									  , root_def, 0, re.UNICODE)
					root_def = re.sub(r'~(\W)', '<i>' + key_full + '</i>\g<1>', root_def, 0, re.UNICODE)
				new_key_section += f'<k>{head_key}</k>'
				all_keys_file.write(head_key + '\n') # TODO sort correctly
		return f'<ar>{new_key_section}<def>{root_def}</def></ar>\n'
	else:
		return newline


def process_tilda_file(filename: str) -> str:
	with open(filename, 'r') as input_f:
		new_filename = add_suffix(filename, 'tilda')
		with open(new_filename, 'w') as output_f, open('wiedza_xdxf_k.txt', 'w') as all_keys_file:
			while True:
				line = input_f.readline()
				if not line:
					break
				line = process_tilda(line, all_keys_file)
				output_f.write(line)
	return new_filename


def process_kref(filename: str) -> str:
	with open(filename, 'r') as input_f:
		new_filename = add_suffix(filename, 'kref')
		with open(new_filename, 'w') as output_f:
			result = input_f.read()
			result = re.sub(r'<ex> </ex>', '', result)
			result = re.sub(r'<ex><pos>ср\.</pos> <b>([^<>]+)</b><b>([^<>]+)</b> </ex>',
							r'<pos>ср.</pos> <kref>\g<1></kref><sup>\g<2></sup>',
							result)  # <k>oblegać</k>
			result = re.sub(r'<ex><pos>ср\.</pos> <b>([^<>]+) (\d+–\d+)</b> </ex>',
							r'<pos>ср.</pos> <kref>\g<1></kref> <co>\g<2></co>',
							result)  # <k>zawier|ać</k>
			result = re.sub(r'<ex><pos>ср\.</pos> <b>([^<>]+) (\d+)</b> </ex>',
							r'<pos>ср.</pos> <kref>\g<1></kref> <co>\g<2></co>',
							result)  # <k>łanowiec</k>
			result = re.sub(r'<ex><pos>ср\.</pos> <b>([^<>]+)</b> </ex>',
							r'<pos>ср.</pos> <kref>\g<1></kref>',
							result)  # <k>wyda|wać, ~ję, ~je</k>

			# without <ex>
			result = re.sub(r'<pos>ср\.</pos> <b>([^<>]+)</b>',
							r'<pos>ср.</pos> <kref>\g<1></kref>',
							result)  # <k>odchylać</k>
			output_f.write(result)
	return new_filename


def add_suffix(filename: str, suffix: str) -> str:
	index = filename.find('.xdxf')
	return filename[0:index] + f"_{suffix}.xdxf"


if __name__ == "__main__":
	newline = """<ar><k>wyda|wać, ~ję, ~je</k><k>wyyyyyd</k><def> <pos>несов.</pos> <def> выдава́ть, дава́ть; отпуска́ть; раздава́ть; </def><def> тра́тить, расхо́довать; </def><def> дава́ть, приноси́ть (<pos>плоды и</pos> <pos>т.п.</pos>); </def><def> выдава́ть, предава́ть; </def><def> издава́ть; оглаша́ть; </def><def> издава́ть, дава́ть; </def><def> дава́ть, устра́ивать; </def><def> издава́ть, испуска́ть <pos>książk.</pos> </def><def> выдава́ть (за́муж) <pos>przest.</pos>; <pos>ср.</pos> <b>wydać</b> </def></def></ar>\n"""
	print(process_tilda(newline))
