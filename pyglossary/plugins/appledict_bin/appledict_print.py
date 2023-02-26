from io import BufferedReader
from typing import List

from pyglossary.plugins.appledict_bin.appledict_file_tools import read_2_bytes


def print_binary(buffer: BufferedReader):
	cursor = buffer.tell()
	for addr_start in range(cursor - 0x40, cursor + 0x40, 2):
		if addr_start == cursor:
			print('\x1b[6;30;42m', end="")
		print_letter(buffer, addr_start)
	buffer.seek(cursor)


def print_buffer_range(buffer: BufferedReader, r: range):
	for c in r:
		print_letter(buffer, c)


def print_letter(buffer: BufferedReader, address):
	i = read_2_bytes(buffer, address)
	CGREYBG = '\x1b[2;30;47m'
	CEND = '\x1b[0m'
	print(f'addr: {CGREYBG}0x{address:6x}{CEND} ({address})  /  value: {CGREYBG}0x_{i:6x}{CEND} ({i})\t\t', end="")
	try:
		if i == 0xa:
			print('\\n')
		else:
			print(chr(i))
	except UnicodeEncodeError:
		print('UNREADABLE')


def pretty_print(cnt: int, addr: int, dt: List[int]):
	print(f'{hex(addr)} #{cnt}:', print_list(dt))


def print_list(l: List) -> str:
	res_str = '['
	res_str += ", ".join(x.__str__() for x in l)
	res_str += ']'
	return res_str
