import requests

from os.path import exists
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def run_searching():
	""" Поиск всех ссылок в разделе с помощью пагинации """
	all_links = []
	stop = False
	while stop == False:
		all_links += find_links()
		stop = next_page()
	return all_links

def find_links():
	""" Возвращает список ссылок на новеллы с текущей 
	    страницы. """
	page_links = []
	found_links = soup.findAll('div', class_="entryBlock")
	for link in found_links:
		page_links.append(link.a["href"])

	return page_links

def next_page(restart=False, skip=False):
	""" Открытие следующей страницы. 
	    Возвращает флаг для остановки парсинга. """
	global URL, page, soup, count_page, headers

	if soup.find('div', class_="pagination") is None:
		return True

	next = soup.find('div', class_="pagination").b.next_sibling.next_sibling

	if next is None:
		return True

	if restart:
		headers = {"User-Agent": UserAgent().random}

	if skip:		
		headers = {"User-Agent": UserAgent().random}
		next = next.next_sibling.next_sibling

	URL = "https://anivisual.net" + next["href"]
	page = requests.get(URL, headers=headers)

	if restart:
		print(f"{count_page}. >> {URL} {page.status_code} RESTART")
		if page.status_code != 200:
			print(f"{count_page}. >> {URL} {page.status_code} SKIP")
			if not next_page(skip=True):
				return False
	elif skip:
		if page.status_code != 200:
			print("FAILED: CANNOT SKIP.")
			return True
		else:
			soup = BeautifulSoup(page.text, "lxml")
			return False
	else:
		count_page += 1
		print(f"{count_page}. >> {URL} {page.status_code}")
		if page.status_code != 200:
			next_page(restart=True)
			return False

		soup = BeautifulSoup(page.text, "lxml")
		return False

	return True


def transform_to_num(link):
	""" Вспомогательная функция, форматирующее число, для 
	    сортировки ссылок в порядке неубывания. """
	first_number = link[link.rfind("/") + 1:link.find("-")]
	end_number = link[link.rfind("-") + 1:]

	result_number = int(first_number + ("0" * (4 - len(end_number)) + end_number))
	return result_number


def add_to_file(links, check=True):
	""" Добавляет новые уникальные ссылки в файл и сортирует их.
	    Опционально: считывает все ссылки для проверки на 
	    уникальность. """
	if exists("links_to_parse.txt") and check:
		with open("links_to_parse.txt", "r") as file:
			for line in file.readlines():
				links.append(line.replace("\n", ""))
	links = list(set(links))
	links = sorted(links, key=transform_to_num)
	print(f"total links: {len(links)}")
	
	with open("links_to_parse.txt", "w") as file:
		for link in links:
			file.write(link + '\n')



def main():
	links = run_searching()
	add_to_file(links)

#START URL input...
URL = "https://anivisual.net/stuff/"
headers = {"User-Agent": UserAgent().random}
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.text, "lxml")

count_page = 1
print(f"{count_page}. >> {URL} {page.status_code}")

if __name__ == "__main__":
	main()