import os
import re
import pprint
import requests

from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def date_transform(date):
	""" Возвращает отформатированные данные типа дата/время """
	month = {
		"Дек": "12", 
		"Ноя": "11",
		"Окт": "10",
		"Сен": "09",
		"Авг": "08",
		"Июл": "07",
		"Июн": "06",
		"Май": "05",
		"Апр": "04",
		"Мар": "03",
		"Фев": "02",
		"Янв": "01"
	}

	for m in month.keys():
		if m in date:
			date = date.replace(m, month[m])
			date = date.replace("/", "-")
	date += ":00"

	return date

def transtext(obj, flag=False, flag_name=False):
	''' Форматирование данных из блока информации.
	    Возвращает строку или список.
	    При флаге срезает последний элемент строки. '''
	obj = obj.text.strip()
	if flag:
		return obj[:-1]

	elif ',' in obj and not flag_name:
		return obj.split(', ') 	
	return obj


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
			bg_url = re.search("/(.+jpg)", bg_url.text).group()
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


def get_description(save_all=True, form_text=True):
	''' Извлечение описания новеллы в строковом формате. 
	    save_all - парсинг скрытых данных и кнопок.
	    form_text - удаление тегов с сохранением текста. '''
	description = soup.find('div', class_='tab-pane active').find('div', 
		attrs={"style": " display:inline-block;padding-top: 20px;"})

	if not save_all:
		while 'uSpoilerClosed' in str(description):
			description.select_one('.uSpoilerClosed').decompose()

	while 'UhideBlockL' in str(description):
		description.select_one('.UhideBlockL').decompose()

	return description.text if form_text == True else str(description)


def get_links():
	""" Получение списка ссылок на скачивание под описанием,
	    получение дополнительных материалов, при наличии. """
	links_list = []
	links = soup.find("div", id="partners").findAll('span')

	for link in links:
		links_list.append(str(link))

	return links_list

def search_info():
	""" Извлечение основной информации о новелле.
	    Название, Оригинальное Название(опц.), Год релиза, 
	    Тип, Жанр, Платформа, Продолжительность и так далее. """
	desc_main = dict()
	desc_main["NAME"] = transtext(soup.find('h1'), flag_name=True)
	desc_main["RAITING"] = float(transtext(soup.find(attrs={"itemprop": "ratingValue"})))

	if soup.find('div', class_='single-goods__top').find('h3') is not None:
		desc_main["SUBNAME"] = transtext(soup.find('h3'), flag_name=True)
	else:
		desc_main["SUBNAME"] = ""

	must_be_list = ["Платформа:", "Тип:", "Теги:", "Жанры:"]
	list_info = soup.findAll('dl')
	for data in list_info:
		key = data.find('span', class_='opt')
		value = data.find('span', class_='val art')
		if key:
			if transtext(key) in ["Дата добавления:", "Дата последнего обновления:"]:
				desc_main[transtext(key, flag=True)] = date_transform(transtext(value))
			elif transtext(key) in must_be_list and not isinstance(transtext(value), list):
				desc_main[transtext(key, flag=True)] = [transtext(value)]
			else:
				desc_main[transtext(key, flag=True)] = transtext(value)

	value = []
	categories = soup.findAll('td')
	for data in categories:
		value.append(data.a.text)
	desc_main["Категории"] = value

	return desc_main

def get_guide():
	""" Возвращает прохождение, если оно есть. """
	guide = soup.find("div", id='delivery').find("span")
	if guide is not None:
		return guide
	return ""

def main():
	''' Функционал парсера не полный. '''
	novell_desc = search_info()
	novell_desc["MAIN_IMAGE"] = get_main_image()
	novell_desc["BG_IMAGE"] = get_bg_image()
	novell_desc["MEDIA"] = get_other_media()
	novell_desc["description"] = get_description(save_all=False, form_text=False)
	novell_desc["download_links"] = get_links()
	novell_desc['guide'] = get_guide()
	pprint.pprint(novell_desc)


#URL = input("Введите ссылку на новеллу... >> ")
URL = "https://anivisual.net/stuff/7-1-0-2430"
headers = {'User-Agent': UserAgent().random} 
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.text, 'html.parser')


if __name__ == '__main__':
	main()

