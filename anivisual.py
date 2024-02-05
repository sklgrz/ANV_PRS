import os
import re
import pprint
import requests

from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def transtext(obj, flag=False):
	''' Форматирование текста из блока информации.
	    При флаге срезает последний элемент строки. '''
	if flag:
		return obj.text.strip()[:-1]
	return obj.text.strip()

def check_dir(photo_path):
	''' Проверяет наличие директорий из пути, при отсутствии 
		создаёт их. 
	    Возвращает относительный путь до итогового файла. '''
	last_path = ""
	photo_path = photo_path[1:].split('/')

	for dir in photo_path[:-1]:
		if not os.path.exists(last_path + dir):
			os.mkdir(last_path + dir)
		last_path += dir + "/"
	return last_path + photo_path[-1]

def write_photo(obj_url):
	''' Принимает неполную ссылку на объект и создаёт его.
	    Возвращает относительный путь до него. '''
	img_obj = requests.get("https://anivisual.net" + obj_url).content
	img_path = check_dir(obj_url)

	with open(img_path, 'wb') as f:
		f.write(img_obj)

	return img_path


def get_main_image():
	''' Извлечение обложки новеллы. '''
	main_img_url = soup.find('div', class_='single-goods__image').img['src']
	final_path = write_photo(main_img_url)

	return final_path

def get_bg_image():
	''' Извлечение фонового изображения (опц.), при его 
	    отсутствии в словаре выводится пустая строка. '''
	bg_url = soup.find('style', attrs={'rel': 'stylesheet'})

	if 'url' in bg_url.text:
		if ".png" in bg_url.text:
			bg_url = re.search("/(.+png)", bg_url.text).group()
		else:
			bg_url = re.search("(.+jpg)", bg_url.text).group()
		final_path = write_photo(bg_url)

		return final_path
	return ""

def get_other_media():
	''' Извлечение медиа-файлов из слайдера. '''
	result_list = []
	media = soup.find('div', class_='fotorama')
	media_urls = media.findAll('a')

	for data in media_urls:
		if 'youtu' in data['href']:
			result_list.append(data['href'])
		else:
			result_list.append(write_photo(data['href']))
	return result_list


def get_description():
	''' Извлечение описания новеллы, без дополнительной информации. '''
	description = soup.find('div', class_='tab-pane active').find('div', 
		attrs={"style": " display:inline-block;padding-top: 20px;"})
	while 'uSpoilerClosed' in str(description):
		description.select_one('.uSpoilerClosed').decompose()
	while 'UhideBlockL' in str(description):
		description.select_one('.UhideBlockL').decompose()

	return description.text

def search_info():
	""" Извлечение основной информации о новелле.
	    Название, Оригинальное Название(опц.), Год релиза, 
	    Тип, Жанр, Платформа, Продолжительность и так далее. """
	desc_main = dict()
	desc_main["NAME"] = transtext(soup.find('h1'))
	desc_main["RAITING"] = transtext(soup.find(attrs={"itemprop": "ratingValue"}))

	if soup.find('div', class_='single-goods__top').find('h3') is not None:
		desc_main["SUBNAME"] = transtext(soup.find('h3'))
	else:
		desc_main["SUBNAME"] = ""

	list_info = soup.findAll('dl')
	for data in list_info:
		key = data.find('span', class_='opt')
		value = data.find('span', class_='val art')
		if key:
			desc_main[transtext(key, flag=True)] = transtext(value)

	return desc_main

def main():
	''' Функционал парсера не полный. '''
	novell_desc = search_info()
	novell_desc["MAIN_IMAGE"] = get_main_image()
	novell_desc["BG_IMAGE"] = get_bg_image()
	novell_desc["description"] = get_description()
	novell_desc['MEDIA'] = get_other_media()
	pprint.pprint(novell_desc)


#URL = input("Введите ссылку на новеллу... >> ")
URL = "https://anivisual.net/stuff/7-1-0-2430"
headers = {'User-Agent': UserAgent().random} 
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.text, 'html.parser')


if __name__ == '__main__':
	main()

