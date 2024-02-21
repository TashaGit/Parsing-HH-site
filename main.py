import requests
from bs4 import BeautifulSoup
import fake_useragent
import json 
import time
import re




def get_links(text):
    ua = fake_useragent.UserAgent()
    data = requests.get(
            url = f"https://hh.ru/search/vacancy?text={text}&from=suggest_post&salary=&ored_clusters=true&page=1",
            #url = f"https://hh.ru/search/vacancy?ored_clusters=true&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&L_save_area=true&area=113&text={text}&page=1",
            headers = {"user-agent": ua.random}
        )
    
    if data.status_code != 200:
        print("Ошибка при получении данных")
    else:
        soup = BeautifulSoup(data.content, "html.parser")

        page_count = int(soup.find("div", attrs={"class": "pager"}).find_all("span", recursive=False)[-1].find("a").find("span").text)

        for page in range(1, page_count+1):
            try:
                data = requests.get(
                        url = f"https://hh.ru/search/vacancy?text={text}&from=suggest_post&salary=&ored_clusters=true&page={page}",
                        #url = f"https://hh.ru/search/vacancy?ored_clusters=true&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&L_save_area=true&area=113&text={text}&page={page}",
                        headers = {"user-agent": ua.random}
                    )
                if data.status_code == 200:
                        soup = BeautifulSoup(data.content, "html.parser")
                        for a in soup.find_all('span',attrs = {"class":"serp-item__title-link-wrapper"}):
                            href = a.find('a').attrs['href']
                            yield f"{href.split('?')[0]}"
            except Exception as e:
                    print(f'{e}')
            time.sleep(1)



def get_vacancy(link):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url = link, 
        headers = {"user-agent":ua.random}
    )
    #проверяем коннект с сайтом
    if data.status_code!=200:
        return
    else: 
        #создаем обьект класса для парсинга
        soup = BeautifulSoup(data.content, "html.parser")


        #начинаем парсинг имени вакансии
        try:
            name = soup.find('h1', attrs={'data-qa':"vacancy-title"}).text
        except:
            name = ""

        #парсим зарплату если есть
        try:
            salary_text = soup.find( attrs={'class': 'vacancy-title'}).text
            clean_salary = re.sub(r'^\D+', '', salary_text).replace("\xa0000","000")
        except:
            clean_salary = ""

        try:
            experience = soup.find(attrs={'class':"vacancy-description-list-item"}).text
        except:
            experience = ""

        try:
            time = soup.find('p', attrs={'class':"vacancy-description-list-item", 'data-qa' :"vacancy-view-employment-mode"}).text
        except:
            time = ""

        try: 
            company = soup.find('span', attrs = {'class': "vacancy-company-name" }).text.replace("\xa0"," ")
        except:
            company = ""

        try:
            city = soup.find('div', attrs={'class':"bloko-text", 'data-qa': "vacancy-serp__vacancy-address"}).text
            address = re.findall(r'\w+', city)[0]
        except:
            address = ""

        try:
            tags = [tag.text for tag in soup.find(attrs={"class":"bloko-tag-list"}).find_all("span",attrs={"class":"bloko-tag__section_text"})]
        except:
            tags = []

        hh_link= link
        
        vacancy = {
            "name": name,
            'salary': clean_salary,
            'experience': experience,
            'time': time,
            "company": company,
            "address": address,
            "tags": tags,
            'hh_link': hh_link,
            }

        return vacancy




if __name__ == "__main__":
    data = []
    for a in get_links('аналитик данных'):
        data.append(get_vacancy(a))
        time.sleep(1)
        with open ('da_21022024.json', 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False )
    print('Parsing is over')
            
