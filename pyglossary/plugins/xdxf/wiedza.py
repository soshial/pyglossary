import re
from typing import Dict, Tuple


def process_tilda(newline: str, all_keys_output_file, inflexion_map: Dict) -> str:
	newline = newline.replace('<opt>', '').replace('</opt>', '')  # TODO process <opt>
	if newline.startswith('<ar>'):
		matches = re.match(r'<ar>(<k>.+</k>)<def>(.+)</def></ar>\n', newline)
		# if newline.startswith('<ar><k>biało</k>'):
		# 	print(matches)
		# 	print(newline[-40:])
		# 	quit()
		if matches is None:
			return newline
		else:
			key_section = matches.groups()[0]  # '<k>wyda|wać, ~ję, ~je</k><k>wyyyyyd</k>'
			all_keys = re.findall('<k>(.+?)</k>', key_section)  # ['wyda|wać, ~ję, ~je', 'wyyyyyd']
			root_def = matches.groups()[1]
			# if len(all_keys) > 1:
			# 	print('all_keys', all_keys)
			new_key_section = ''
			for key in all_keys:
				# @key - original key from xdxf: "wyda|wać, ~ję, ~je", "ciągn|ąć się"
				if '|' in key or ',' in key:  # cleaning dictionary keys from powszechny
					if ',' in key:
						root_def = f'<gr><b>{key.replace("|", "")}</b></gr>' + root_def
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
					if key.endswith(' się'):
						key_stem = key[:-4]
						key_full = key[:-4]
					else:
						key_stem = head_key
						key_full = head_key
				if '~' in newline:
					# <ex> <b>odzyskać ~</b> прийти́ в себя́, очну́ться;</ex>
					# <ex> <b>odzyskać <mrkd>świadomość</mrkd></b> прийти́ в себя́, очну́ться;</ex>
					root_def = re.sub(r'~(\w+)', f'<mrkd>{key_stem}\g<1></mrkd>', root_def, re.UNICODE)

					# <ex> <b>~ na własne oczy</b> ви́деть свои́ми глаза́ми;</ex>
					# <ex> <b><mrkd>widzieć</mrkd> na własne oczy</b> ви́деть свои́ми глаза́ми;</ex>
					root_def = re.sub(r'~(\W)', f'<mrkd>{key_full}</mrkd>\g<1>', root_def, 0, re.UNICODE)

					# <ex><b>często się <mrkd>badać</mrkd></b> .... </ex>
					# <ex><b>często <mrkd>się badać</mrkd></b> .... </ex>
					if key.endswith(' się'):
						root_def = re.sub(r'się <mrkd>', '<mrkd>się ', root_def, 0, re.UNICODE)
						root_def = re.sub(r'</mrkd> się', ' się</mrkd>', root_def, 0, re.UNICODE)
				# TODO multi-line <ex>
				# dobrze (źle) ~ kogoś, coś
				# а) хорошо́ (пло́хо) принима́ть кого-л.,что-л.;
				# б) быть хоро́шего (плохо́го) мне́ния о ком-л.,чём-л.;
				# <ex> <b>dobrze (źle) ~</b> <pos>kogoś, coś</pos></ex> <ex> а) хорошо́ (пло́хо) принима́ть <pos>кого-л.</pos>, <pos>что-л.</pos>;</ex> <ex> б) быть хоро́шего (плохо́го) мне́ния о <pos>ком-л.</pos>, <pos>чём-л.</pos>;</ex>

				new_key_section += f'<k>{head_key}</k>'
				all_keys_output_file.write(head_key + '\n')

				if head_key in inflexion_map:
					for wordform in inflexion_map[head_key]:
						if wordform and wordform != head_key:
							new_key_section += f'<k>{wordform}</k>'
				# TODO some are errors
				# wiedza from berk_bear didn't have declension for reflexive
				if head_key.endswith(' się'):
					non_reflexive = head_key[:-4]
					if non_reflexive in inflexion_map:
						for wordform in inflexion_map[non_reflexive]:
							if wordform and wordform != non_reflexive:
								new_key_section += f'<k>{wordform} się</k>'

		return f'<ar>{new_key_section}<def>{root_def}</def></ar>\n'
	else:
		return newline


def split_ex(input_line: str, ex_without_b_tag: int) -> Tuple["ExampleData", int]:
	# <ex> <b>mile ~iany (gość</b> <pos>itp.</pos><b>)</b> жела́нный (гость <pos>и</pos> <pos>т.п.</pos>);</ex>
	# this removes cases where <pos> tag interrupts </b> <b>
	# <ex> <b>~ smutkiem</b> напо́лнить гру́стью;</ex>
	# <ex> <pos>coś</pos> <b>idzie jak z kamienia (jak po grudzie)</b> <pos>что-л.</pos> даётся с больши́м трудо́м;</ex>
	# <ex> <b>alkohol (wódka</b> <pos>itp.</pos><b>) idzie do głowy</b> алкого́ль (во́дка <pos>и</pos> <pos>т.п.</pos>) ударя́ет в го́лову (в но́ги);</ex>
	# <ex> <b>~ w parze</b> <pos>z czymś</pos> сопровожда́ться <pos>чем-л.</pos>, сочета́ться <pos>с чем-л.</pos>;</ex>
	if input_line.find('<kref>') != -1:
		# ex_without_b_tag += 1
		result = input_line.removeprefix('<ex>').removesuffix('</ex>')
		return ExampleData(was=input_line, now=result, has_b=False), ex_without_b_tag
	if input_line.find('</b>') == -1:
		ex_without_b_tag += 1
		return ExampleData(was=input_line, now=input_line, has_b=False), ex_without_b_tag
	include_pos_into_ex_orig = re.sub(r'</b>(\s*<pos>[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż,.\s]+</pos>)', '\g<1></b>', input_line)
	include_pos_into_ex_orig = re.sub(r'</b>(\s*<pos>[^<]+</pos>)</ex>', '\g<1></b></ex>', include_pos_into_ex_orig)
	first_part, last_part = include_pos_into_ex_orig.rsplit('</b>', 1)
	first_part = first_part.removeprefix('<ex>')
	last_part = last_part.removesuffix('</ex>')
	first_part = first_part.replace('<b>', '').replace('</b>', '')
	result = f'<ex><ex_orig>{first_part}</ex_orig><ex_tran>{last_part}</ex_tran></ex>'
	result = result.replace('<ex_tran> ', ' <ex_tran>')
	return ExampleData(was=input_line, now=result, has_b=True), ex_without_b_tag


class ExampleData:
	def __init__(self, was: str, now: str, has_b: bool):
		self.was = was
		self.now = now
		self.has_b = has_b

	def __str__(self, *args, **kwargs):
		return f"ExampleData(was=`{self.was}`,now=`{self.now}`,has_b=`{self.has_b}`)"


def process_ex(line: str, ex_without_b_tag: int) -> Tuple[str, int]:
	is_only_orig = lambda s: '<ex_tran></ex_tran></ex>' in s
	is_only_tran = lambda s: '<ex_orig>' not in s and \
							 '<ex_tran>' not in s and \
							 re.search(r'<ex> ?[абвгде]\)', s) is not None
	letters = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з']

	examples = re.findall(r'(<ex>.+?</ex>)', line)
	examples_replacements = []
	for ex in examples:
		ex_data, ex_without_b_tag = split_ex(ex, ex_without_b_tag)
		examples_replacements.append(ex_data)

	# merge multiline <ex> into a single one
	for i in range(len(examples_replacements) - 2):
		if is_only_orig(examples_replacements[i].now) and \
				is_only_tran(examples_replacements[i + 1].now) and \
				is_only_tran(examples_replacements[i + 2].now):
			ex_without_b_tag -= 2
			# print(examples_replacements[i][1], '\n', examples_replacements[i + 1][1], '\n',
			# 	  examples_replacements[i + 2][1], '\n\ninto ->\n')
			ex_orig = examples_replacements[i].now.replace('<ex_tran></ex_tran></ex>', '')
			ex_tran1 = re.sub(r'<ex> ?[абвгде]\)', '<ex_tran>', examples_replacements[i + 1].now).replace(
				'</ex>', '</ex_tran>')
			ex_tran2 = re.sub(r'<ex> ?[абвгде]\)', '<ex_tran>', examples_replacements[i + 2].now).replace(
				'</ex>', '</ex_tran>')
			examples_replacements[i + 2].now = ''
			examples_replacements[i + 1].now = ''
			examples_replacements[i].now = f'{ex_orig}{ex_tran1}{ex_tran2}</ex>'
	for ex_data in examples_replacements:
		if ex_data.now.find('<ex>') != -1 and ex_data.was.find('</b>') == -1 and ex_data.now.find('<mrkd>') == -1:
			print(ex_data.now)
	for ex_data in examples_replacements:
		line = line.replace(ex_data.was, ex_data.now)
	return line, ex_without_b_tag


def process_tilda_file(filename: str) -> str:
	new_filename = add_suffix(filename, 'tilda')
	with open(filename, 'r') as input_f:
		with open(new_filename, 'w') as output_f, \
				open('wiedza_xdxf_k.txt', 'w') as all_keys_output_file, \
				open('wiedza-berk-bear.txt', 'r') as inflexion_keys_file:

			inflexion_map = {}

			while True:
				line = inflexion_keys_file.readline()
				if not line:
					break
				wordforms = line.strip().split(',')
				inflexion_map[wordforms[0]] = wordforms[1:]

			ex_without_b_tag = 0

			while True:
				line = input_f.readline()
				if not line:
					break
				line = process_tilda(line, all_keys_output_file, inflexion_map)
				line, ex_without_b_tag = process_ex(line, ex_without_b_tag)
				output_f.write(line)
			print('____ex_without_b_tag', ex_without_b_tag)
	return new_filename


def process_kref(filename: str) -> str:
	with open(filename, 'r') as input_f:
		new_filename = add_suffix(filename, 'kref')
		with open(new_filename, 'w') as output_f:
			result = input_f.read()
			result = resub(r'<ex> </ex> <ex>(.+)</ex></def>', '</def>\g<1>', result)  # TODO см. статью "а"
			result = resub(r'<ex> ?◊ (.+)</ex> ?</def></def>', '</def><ex> ◊ \g<1></ex></def>', result)
			result = resub(r'<ex><pos>ср\.</pos> <b>([^<>]+)</b><b>([^<>]+)</b> </ex>',
						   r'<pos>ср.</pos> <kref>\g<1></kref><sup>\g<2></sup>',
						   result)  # <k>oblegać</k>
			result = resub(r'<ex><pos>ср\.</pos> <b>([^<>]+) (\d+–\d+)</b> </ex>',
						   r'<pos>ср.</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)  # <k>zawier|ać</k>
			result = resub(r'<ex><pos>ср\.</pos> <b>([^<>]+) (\d+-\d+)</b> </ex>',
						   r'<pos>ср.</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)  # <k>zawier|ać</k>
			result = resub(r'<ex><pos>ср\.</pos> <b>([^<>]+) (\d+)</b> </ex>',
						   r'<pos>ср.</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)  # <k>łanowiec</k>
			result = resub(r'<ex><pos>ср\.</pos> <b>([^<>]+)</b> </ex>',
						   r'<pos>ср.</pos> <kref>\g<1></kref>',
						   result)  # <k>wyda|wać, ~ję, ~je</k>

			# without <ex>
			# <pos>ср.</pos> <kref>darować 1–3</kref>
			# <pos>ср.</pos> <kref>darować</kref> <co>1–3</co>
			result = resub(r'ср\.</pos> <b>([^<>]+) (\d+–\d+)</b>',
						   r'ср.</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)
			result = resub(r'ср\.</pos> <b>([^<>]+) (\d+-\d+)</b>',
						   r'ср.</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)
			result = resub(r'ср\.</pos> <b>([^<>]+) (\d+)</b>',
						   r'ср.</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)
			result = resub(r'ср\.</pos> <b>([^<>]+)</b>',
						   r'ср.</pos> <kref>\g<1></kref>',
						   result)  # <k>odchylać</k>

			# см.</pos> <b>nędza 1–3</b>
			# см.</pos> <kref>nędza</kref> <co>1–3</co>
			result = resub(r'см\.</pos> <b>([^<>]+) (\d+–\d+)</b>',
						   r'см.</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)
			result = resub(r'см\.</pos> <b>([^<>]+) (\d+-\d+)</b>',
						   r'см.</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)
			# <pos>см.</pos> <b>bombowy 2</b>
			# <pos>см.</pos> <kref>bombowy</kref> 2
			result = resub(r'см\.</pos> <b>([^<>]+) (\d+)</b>',
						   r'см.</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)

			# <ar><k>awiomatka</k><def> <pos>ж. разг. см.</pos> <b>lotniskowiec</b> </def></ar>
			result = resub(r'см\.</pos> <b>([^<>]+)</b>',
						   r'см.</pos> <kref>\g<1></kref>',
						   result)
			# <pos>сущ. от</pos> <kref>sprzątać 3–5</kref>
			result = resub(r'от</pos> <b>([^<>]+) (\d+–\d+)</b>',
						   r'от</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)
			# <ar><k>bolejący</k><def> <def> <pos>прич. от</pos> <b>boleć 2</b>
			# <ar><k>bolejący</k><def> <def> <pos>прич. от</pos> <kref>boleć</kref> <co>2</co>
			result = resub(r'от</pos> <b>([^<>]+) (\d+)</b>',
						   r'от</pos> <kref>\g<1></kref> <co>\g<2></co>',
						   result)

			# <ar><k>rozegran|y</k><def><def> <pos>прич. от</pos> <b>rozegrać</b>; </def>
			result = resub(r'от</pos> <b>([^<>]+)</b>',
						   r'от</pos> <kref>\g<1></kref>',
						   result)
			output_f.write(result)
	return new_filename


def resub(pattern, repl, string) -> str:
	(result, subs_made) = re.subn(pattern, repl, string)
	print(f'    {subs_made}: {pattern} -> {repl}')
	return result


# // todo добавить остальные аббревиатуры
# // улучшаем отображение аббревиатур
# //
# // гг.— годы — lata
# // гидр. — гидрология, гидротехника — hydrologia, hydrotechnika
# // дееприч.— деепричастие — imiesłów przysłówkowy
# // доп.— дополнение — dopełnienie
# // кг — килограмм — kilogram
# // км — километр — kilometr
# // -л.— либо — -kolwiek
# // личн.— 1) личная форма; 2) личное (местоимение) — l) forma osobowa; 2) zaimek osobowy
# // метр — metr
# // мм — миллиметр — milimetr
# // отглаг.— отглагольный — odczasownikowy
# // п.— падеж — przypadek
# // полигр.— полиграфия — poligrafia
# // р.— род — rodzaj
# // соотв.— соответствует — odpowiada
# // сочет.— сочетание — połączenie
# // тех.— техника — technika
# // ф.— форма — forma
# // ч.— число — liczba
abrewiatury = [
	# // сокр.—сокращение, сокращенно—skrót, skrótowo
	[None, 'возвр.', None, 'возвратное'],
	[None, 'библ.', None, 'библейское, библеистика'],
	[None, 'неопр.', '1) bezokolicznik; 2) zaimek nieokreślony',
	 '1) неопределённая форма глагола; 2) неопределённое местоимение'],
	['bezok.', None, 'bezokolicznik', 'неопределенная форма глагола'],
	['nieokr.', None, 'nieokreślony', 'неопределенный'],
	['okr.', None, 'określający', 'определительный'],
	[None, 'сокр. от', None, 'сокращение от...'],
	[None, 'в сочет.', None, 'в сочетании с...'],
	[None, 'личн.', None, 'личное местоимение'],
	[None, 'рим.', None, 'история и культура Римской Империи'],
	[None, 'тк.', 'tylko', 'только'],
	[None, 'телев.', None, 'телевидение и телевещание'],
	[None, 'р.', None, 'река'],
	[None, 'психол.', None, 'психология'],
	[None, 'информ.', None, 'информатика и программирование'],
	[None, 'фото', None, 'фотография и фототехника'],
	[None, 'в знач.', None, 'в значении чего:'],
	[None, 'геом.', None, 'геометрия'],
	['posp.', None, 'pospolite słowo: cechujący się odrobiną wulgarności, ordynarności', 'вульгаризм, просторечие'],
	[None, '1 л.', None, 'употребляется в 1-м лице'],
	[None, '3 л.', None, 'употребляется в 3-м лице'],
	[None, 'тж.', 'również', 'также'],
	[None, 'буд.', 'czas przyszły', 'будущее время'],
	[None, 'прош.', 'czas przeszły', 'прошедшее время'],
	['anat.', 'анат.', 'anatomia', 'анатомия'],
	['antr.', 'антр.', 'antropologia', 'антропология'],
	['archeol.', 'археол.', 'archeologia', 'археология'],
	['archit.', 'архит.', 'architektura', 'архитектура'],
	['astr.', 'астр.', 'astronomia', 'астрономия'],
	['B.', 'вин.', 'biernik', 'винительный падеж'],
	['bdop.', None, 'bez dopełnienia', 'без дополнения'],
	['bier.', None, 'bierny', 'страдательный'],
	['biol.', 'биол.', 'biologia', 'биология'],
	['biur.', 'канц.', 'biurowy', 'канцеляризм'],
	['blm.', None, 'bez liczby mnogiej', 'без множественного числа'],
	['blp.', None, 'bez liczby pojedynczej', 'без единственного числа'],
	['bot.', 'бот.', 'botanika', 'ботаника'],
	['bud.', 'стр.', 'budownictwo', 'строительное дело'],
	['C.', 'дат.', 'celownik', 'дательный падеж'],
	['cerk.', 'церк.', 'cerkiewny', 'церковное слово, выражение'],
	['chem.', 'хим.', 'chemia', 'химия'],
	['cz.', 'вр.', 'czas', 'время'],
	['cz. ter.', 'наст.', 'czas teraźniejszy', 'настоящее  время'],
	['czas.', 'гл.', 'czasownik', 'глагол'],
	['D.', 'род.', 'dopełniacz', 'родительный падеж'],
	['dezapr.', 'неодобр.', 'z dezaprobatą', 'неодобрительно'],
	['dk', 'сов.', 'dokonany', 'совершенный вид глагола'],
	['druk.', 'полигр.', 'drukarstwo', 'печатное дело'],
	['dypl.', 'дип.', 'dyplomatyczny', 'дипломатический термин'],
	['dźwiękonaśl.', None, 'dżwiękonaśladowczy', 'звукоподражательное слово'],
	['ekon.', 'эк.', 'ekonomia', 'экономика'],
	['el.', 'эл.', 'elektrotechnika', 'электротехника'],
	['emfat.', 'высок.', 'emfatyczny', 'высокопарное выражение'],
	['etn.', None, 'etnografia', 'этнография'],
	[None, 'эвф.', None, 'эвфемизм'],
	['farm.', 'фарм.', 'farmacja', 'фармацевтический термин'],
	['film.', 'кино ', 'film, filmowy', 'кинематография'],
	['filol.', 'филол.', 'filologia', 'филология'],
	['filoz.', 'филос.', 'filozofia', 'философия'],
	['fin.', 'фин.', 'finansowy', 'финансовый термин'],
	['fiz.', 'физ.', 'fizyka', 'физика'],
	['fizjol.', 'физиол.', 'fizjologia', 'физиология'],
	['f. dł.', None, 'forma długa', 'полная форма'],
	['f. kr.', None, 'forma krótka (ucięta)', 'краткая форма'],
	['folkl.', 'фольк.', 'folklor', 'фольклор'],
	['fot.', 'фото ', 'fotografia, fotografika', 'фотография'],
	['geod.', 'геод.', 'geodezja', 'геодезия'],
	['geogr.', 'геогр.', 'geografia', 'география'],
	['geol.', 'геол.', 'geologia', 'геология'],
	['gm.', 'прост.', 'gminny', 'просторечие'],
	['górn.', 'горн.', 'górnictwo', 'горное дело'],
	['górnol.', None, 'górnolotny', 'высокий стиль'],
	[None, 'греч.', 'grecki', 'греческий'],
	[None, 'итал.', 'włoski', 'итальянский'],
	[None, 'лат.', 'łaciński', 'латинский'],
	['gram.', 'грам.', 'gramatyka', 'грамматика'],
	['gw', 'обл.', 'gwarowy', 'местное выражение, диалектизм'],
	['hand.', 'торг.', 'handel', 'торговля'],
	['hist.', 'ист.', 'historia', 'история'],
	['hutn.', None, 'hutnictwo', 'металлургия'],
	['imiesł.', 'прич.', 'imiesłów', 'причастие'],
	['iron.', 'ирон.', 'ironicznie', 'в ироническом смысле'],
	['itd.', 'и т.д.', 'i tak dalej', 'и так далее'],
	['itp.', 'и т.п.', 'i tym podobne', 'и тому подобное'],
	['jkr.', 'однокр.', 'jednokrotny', 'однократный вид глагола'],
	['karc.', 'карт.', 'wyrażenie karciane', 'термин карточной игры'],
	['kol.', 'ж.–д.', 'kolejnictwo', 'железнодорожное дело'],
	['książk.', 'книжн.', 'książkowy', 'книжный стиль'],
	['księg.', 'бухг.', 'księgowość', 'бухгалтерия'],
	['kulin.', 'кул.', 'kulinarny', 'кулинария'],
	['lekcew.', 'пренебр.', 'lekceważąco', 'пренебрежительно'],
	['leśn.', 'лес.', 'leśnictwo', 'лесное дело'],
	['licz.', 'числ.', 'liczebnik', 'имя числительное'],
	['lingw.', 'лингв.', 'lingwistyka', 'лингвистика'],
	['lit.', 'лит.', 'literatura', 'литература'],
	['lm', 'мн.', 'liczba mnoga', 'множественное число'],
	['log.', 'лог.', 'logika', 'логика'],
	['lotn.', 'ав.', 'lotnictwo', 'авиация'],
	['lp', 'ед.', 'liczba pojedyncza', 'единственное число'],
	['M.', 'им.', 'mianownik', 'именительный падеж'],
	['m.-o.', 'л.–м. ф.', 'męskoosobowa forma', 'лично-мужская форма'],
	['mat.', 'мат.', 'matematyka', 'математика'],
	['med.', 'мед.', 'medycyna', 'медицина'],
	['meteor.', 'метеор.', 'meteorologia', 'метеорология'],
	['miern.', None, 'miernictwo', 'метрология'],
	['miner.', 'мин.', 'mineralogia', 'минералогия'],
	['mit.', 'миф.', 'mitologia', 'мифология'],
	['mor.', 'мор.', 'morski, żeglarstwo', 'морское дело, морской термин'],
	['Ms.', 'предл.', 'miejscownik', 'предложный падеж'],
	['muz.', 'муз.', 'muzyka', 'музыка'],
	['myśl.', 'охот.', 'myślistwo', 'охотничий термин'],
	['N.', 'твор.', 'narzędnik', 'творительный падеж'],
	['ndk', 'несов.', 'niedokonany', 'несовершенный вид глагола'],
	['ndm', 'нескл.', 'nieodmienny', 'несклоняемое слово'],
	['nieos.', 'безл.', 'nieosobowo, nieosobowy', 'безличная форма'],
	['np.', 'напр.', 'na przykład', 'например'],
	['obelż.', 'бран.', 'obelżywy', 'бранное слово, выражение'],
	['ofic.', 'офиц.', 'oficjalny', 'официальный термин, официальное выражение'],
	['ogr.', 'сад.', 'ogrodnictwo', 'садоводство'],
	['opt.', 'опт.', 'optyka', 'оптика'],
	['orzecz.', 'сказ.', 'orzeczenie', 'сказуемое'],
	['os.', 'л.', 'osoba', 'лицо глагола'],
	['osob.', None, 'osobowy', 'личный'],
	['paleont.', 'палеонт.', 'paleontologia', 'палеонтология'],
	['part.', 'частица', 'partykuła', 'частица'],
	['ped.', 'педаг.', 'pedagogika', 'педагогика'],
	['pejor.', None, 'pejoratywny', 'уничижительная форма'],
	['pieszcz.', 'ласк.', 'pieszczotliwy', 'уменьшительно-ласкательная форма'],
	['poet.', 'поэт.', 'poetycki', 'поэтическое слово'],
	['poez. lud.', None, 'poezja ludowa', 'народно-поэтическое слово, выражение'],
	['pogard.', 'презр.', 'pogardliwie', 'презрительно'],
	['polit.', 'полит.', 'polityka', 'политический термин'],
	['pot.', 'разг.', 'potoczny', 'разговорное слово, выражение'],
	['pouf.', 'фам.', 'poufały', 'фамильярное слово, выражение'],
	['praw.', 'юр.', 'prawo, prawniczy', 'юридический термин'],
	['przecz.', 'отриц.', 'przeczenie', 'отрицание'],
	['przen.', 'перен.', 'przenośnie, przenośnia', 'в переносном значении'],
	[None, 'прям.', None, 'в прямом значении'],
	['przest.', 'уст.', 'przestarzały', 'устаревшее слово, выражение'],
	['przyim.', 'предлог', 'przyimek', 'предлог'],
	['przym.', 'прил.', 'przymiotnik', 'имя прилагательное'],
	['przysł.', 'нареч.', 'przysłówek', 'наречие'],
	['przys.', 'посл.', 'przysłówie', 'пословица'],
	[None, 'погов.', None, 'поговорка'],
	['psychol.', 'псих.', 'psychologia', 'психология'],
	['pszczel.', 'пчел.', 'pszczelarstwo', 'пчеловодство'],
	['rad.', 'радио ', 'radiotechnika, radiofonia', 'радиотехника'],
	['reg.', 'рег.', 'regionalny', 'областное слово, выражение'],
	['rel.', 'рел.', 'religia', 'религия'],
	['rol.', 'с.–х.', 'rolnictwo', 'сельское хозяйство'],
	['rozk.', 'повел.', 'tryb rozkazujący', 'повелительное наклонение'],
	['ryb.', 'рыб.', 'rybołówstwo', 'рыболовство, рыбоводство'],
	['rzad.', 'редко', 'rzadko używane słowo czy forma', 'редкое слово или словоформа'],
	['rzecz.', 'сущ.', 'rzeczownik', 'имя существительное'],
	['sam.', 'авт.', 'samochodowe', 'автомобильный термин'],
	['spec.', 'спец.', 'specjalny', 'специальный термин'],
	['sport.', 'спорт.', 'sport, sportowy', 'физкультура и спорт'],
	['spójn.', None, 'spójnik', 'союз'],  # todo обработать союзы
	['stn.', 'превосх. ст.', 'stopień najwyższy', 'превосходная степень'],
	['stw.', 'сравнит. ст.', 'stopień wyższy', 'сравнительная степень'],
	['szach.', 'шахм.', 'szachowy', 'термин шахматной игры'],
	['szt.', 'иск.', 'sztuka', 'искусство'],
	['teatr.', 'театр.', 'teatralny, teatrologia', 'театральный термин, театроведение'],
	['tech.', 'тех.', 'techniczny', 'технический термин'],
	['uczn.', 'школ.', 'uczniowski', 'школьное слово, выражение'],
	['uż.', 'употр.', 'używa się', 'употребляется'],
	['W.', 'зват.', 'wolacz', 'звательный падеж'],
	['w.', 'в.', 'wiek', 'век'],
	['wet.', 'вет.', 'weterynaria', 'ветеринария'],
	['włók.', 'текст.', 'włókiennictwo', 'текстильное дело'],
	['woj.', 'воен.', 'wojskowość', 'военное дело, военный термин'],
	['wkr.', 'многокр.', 'wielokrotny', 'многократный вид глагола'],
	['wskaz.', 'указ.', 'wskazujący', 'указательный'],
	['wulg.', 'груб.', 'wulgarny', 'грубое слово, вульгаризм'],
	['wykrz.', 'межд.', 'wykrzyknik', 'междометие'],
	['wyr. wtrąc.', None, 'wyraz wtrącony', 'вводное слово'],
	['wzgl.', 'относ.', 'zaimek względny', 'относительное местоимение'],
	[None, 'вопр.', None, 'вопросительное местоимение'],
	['zaim.', 'мест.', 'zaimek', 'местоимение'],
	['zbior.', 'собир.', 'zbiorowy (rzeczownik, liczebnik)', 'собирательное (существительное, числительное)'],
	['zdr.', None, 'zdrobniały', 'уменьшительная форма'],
	['zdr.-pieszcz.', 'уменьш.', 'zdrobniało-pieszczotliwy', 'уменьшительно-ласкательная форма'],
	['zgr.', 'увелич.', 'zgrubiały', 'увеличительная форма'],
	['zn.', None, 'znaczenie', 'значение'],
	['zob.', 'см.', 'zobacz', 'смотри'],
	['zool.', 'зоол.', 'zoologia', 'зоология'],
	['żarg.', 'жарг.', 'żargonowy, argotyzm', 'жаргонное слово, выражение'],
	['żart.', 'шутл.', 'żartobliwy', 'шутливое слово, выражение'],
	['ż', 'ж.', 'rodzaj żeński', 'женский род'],
	['m', 'м.', 'rodzaj męski', 'мужской род'],
	['n', 'с.', 'rodzaj nijaki', 'средний род'],
	['g', 'г', 'gram', 'грамм'],
	['r.', 'г.', 'rok', 'год'],
	[None, 'фр.', None, 'образовано от французского'],
	[None, 'англ.', None, 'образовано от английского'],
	[None, 'нем.', None, 'образовано от немецкого'],
	['cf.', 'ср.', 'porównaj z', 'сравни с'],
]


def process_pos(filename: str) -> str:
	abbr_map_keys = []
	abbr_xdxf_string = '  <abbreviations>\n'
	for row in abrewiatury:
		pl_short, ru_short, pl_full, ru_full = row
		abbr_xdxf_string += '    <abbr_def>'
		if pl_short is not None:
			abbr_xdxf_string += f'<abbr_k>{pl_short}</abbr_k>'
			abbr_map_keys.append(pl_short)
		if ru_short is not None:
			abbr_xdxf_string += f'<abbr_k>{ru_short}</abbr_k>'
			abbr_map_keys.append(ru_short)
		abbr_v = '<abbr_v>'
		if pl_full is not None:
			abbr_v += f'{pl_full}<br/>'
		if ru_full is not None:
			abbr_v += f'{ru_full}<br/>'
		abbr_v = abbr_v.strip()
		abbr_v += '</abbr_v>'

		abbr_xdxf_string += abbr_v
		abbr_xdxf_string += '</abbr_def>\n'
	abbr_xdxf_string += '  </abbreviations>'

	abbr_key_regex = '|'.join(abbr_map_keys).replace('.', '\.')

	# TODO <ex> <b>I</b>
	# TODO r"</b> <pos>[^<]+</pos></ex>"
	# TODO <ar><k>pro</k><def> <b>: ~ i kontra</b> про и ко́нтра, за и про́тив </def></ar>

	with open(filename, 'r') as input_f:
		new_filename = add_suffix(filename, 'pos')
		with open(new_filename, 'w') as output_f:
			result = input_f.read()
			# TODO ISC: <ex> <pos>coś</pos> <b>idzie jak z kamienia (jak po grudzie)</b> <pos>что-л.</pos> даётся с больши́м трудо́м;</ex>
			result = re.sub(r'</meta_info>', f'{abbr_xdxf_string}\n</meta_info>', result)
			result = resub(r'<co> ', r' <co>', result)
			result = resub(r'<pos>т</pos>', r'<abbr>m</abbr>', result)
			result = resub(r'<pos>т,</pos>', r'<abbr>m</abbr>,', result)
			result = resub(r'<pos>сравнит.</pos> <pos>ст\.', r'<abbr>сравнит. ст.</abbr> <pos>', result)
			result = resub(r'с\.</pos>–<pos>х\.</pos>', r'с.–х.</pos>', result)
			result = resub(r'ж\.</pos>–<pos>д\.</pos>', r'ж.–д.</pos>', result)
			result = resub(r'л\.</pos>–<pos>м\.</pos>', r'л.–м.</pos>', result)
			result = resub(r'уменьш\.</pos>-<pos>ласк\.', r'уменьш.-ласк.', result)
			result = resub(r' </pos>', r'</pos> ', result)
			result = resub(r'<pos> ', r' <pos>', result)
			result = resub(r'<pos>л.</pos><i>–</i><pos>м.</pos> <pos>ф.</pos>', r'<abbr>л.–м. ф.</abbr>', result)
			result = resub(r'<pos>л.</pos><i>–</i><pos>м.</pos> <pos>ф.', r'<abbr>л.–м. ф.</abbr> <pos>', result)
			result = resub(r'и</pos> <pos>т.п.</pos>', r'и т.п.</pos>', result)
			result = resub(r'и</pos> <pos>т.д.</pos>', r'и т.д.</pos>', result)

			result = resub(r'</i> <pos>([^<>()]*)</pos>\)', r' <pos>\g<1></pos></i>)', result)
			result = resub(r' и</i> <pos>т.п.</pos>', r' <pos>и т.п.</pos></i>', result)
			result = resub(f' ({abbr_key_regex})</pos>', r'</pos> <abbr>\g<1></abbr>', result)
			result = resub(f' ({abbr_key_regex})</pos>', r'</pos> <abbr>\g<1></abbr>', result)
			result = resub(f' ({abbr_key_regex})</pos>', r'</pos> <abbr>\g<1></abbr>', result)
			result = resub(f'<pos>({abbr_key_regex})</pos>', r'<abbr>\g<1></abbr>', result)
			result = resub(f'<pos>({abbr_key_regex}) ', r'<abbr>\g<1></abbr> <pos>', result)
			result = resub(f'<pos>({abbr_key_regex}) ', r'<abbr>\g<1></abbr> <pos>', result)
			result = resub(f'<pos>({abbr_key_regex}) ', r'<abbr>\g<1></abbr> <pos>', result)
			result = resub(r'<pos>м</pos>', r'<abbr>м.</abbr>', result)
			result = resub(r'<pos>blm</pos>', r'<abbr>blm.</abbr>', result)
			result = resub(r'<pos>blp</pos>', r'<abbr>blp.</abbr>', result)
			comment_sections = re.findall(r'\(<i>[^()]+</i>\)', result)
			for comment_orig in comment_sections:
				comment_fixed = comment_orig.replace('</i>)', '</co>').replace('(<i>', '<co>')
				comment_fixed = comment_fixed.replace('<i>', '').replace('</i>', '')
				result = result.replace(comment_orig, comment_fixed)
			output_f.write(result)
	return new_filename


def add_suffix(filename: str, suffix: str) -> str:
	index = filename.find('.xdxf')
	return filename[0:index] + f"_{suffix}.xdxf"


if __name__ == "__main__":
	ex_data, b = split_ex(
		'<ex> <b>być przykutym</b> <pos>do czyjegoś</pos> <b>~u</b> быть прико́ванным <pos>к кому-л.</pos>, идти́ на поводу́ <pos>у кого-л.</pos> </ex>',
		0)
	print(ex_data)

# from pyglossary import slob
#
# writer = slob.Writer('/Users/soshial/Downloads/slob/conversion_output/wiedza_pl-ru_2024-05-07_soshial_css.slob')
# with open('/Users/soshial/PycharmProjects/pyglossary/pyglossary/xdxf/xdxf.css', 'rb') as css_file:
# 	writer.add(css_file.read(), 'css/xdxf.css', content_type='text/css')
#
# with slob.open('/Users/soshial/Downloads/slob/conversion_output/wiedza_pl-ru_2024-05-07_soshial.slob') as reader:
# 	tags = dict(reader.tags.items())
# 	print(tags)
# 	print(reader.content_types)
# 	i = 0
# 	for blob in reader:
# 		writer.add(blob.content, blob.key)
# 		if 'xdxf' in blob.key:
# 			print('finally!')
# 			quit()
# 		i += 1
# writer.finalize()

# with writer as w:

# def p(blob):
# 	print(blob.content_type, blob.content, '\n')
#
# for key in ('xdxf.css'):
# 	blob = next(r.as_dict()[key])
# 	p(blob)

# p(next(r.as_dict()['mars']))
# newline = """<ar><k>wyda|wać, ~ję, ~je</k><k>wyyyyyd</k><def> <pos>несов.</pos> <def> выдава́ть, дава́ть; отпуска́ть; раздава́ть; </def><def> тра́тить, расхо́довать; </def><def> дава́ть, приноси́ть (<pos>плоды и</pos> <pos>т.п.</pos>); </def><def> выдава́ть, предава́ть; </def><def> издава́ть; оглаша́ть; </def><def> издава́ть, дава́ть; </def><def> дава́ть, устра́ивать; </def><def> издава́ть, испуска́ть <pos>książk.</pos> </def><def> выдава́ть (за́муж) <pos>przest.</pos>; <pos>ср.</pos> <b>wydać</b> </def></def></ar>\n"""
