import requests
import json
from utils.scraping.beautiful_soup import BeautifulSoup, get_text_from_bs
from datetime import timedelta, datetime


class VaticanScraper:
    def __init__(self, language="fr"):
        self.base_url = "http://w2.vatican.va/content/francesco/"
        self.language = language

    def get_content_index(self, content_type="homilies"):
        whole_index = list()
        for year in [2013, 2014, 2015, 2016, 2017, 2018]:
            complete = False
            while not complete:
                page = 1
                url = "{}/{}/{}/{}.index.{}.html"\
                    .format(self.base_url, self.language, content_type, year, page)
                res = requests.get(url)
                bs = BeautifulSoup(res.content, 'html.parser')
                index = bs.find("div", class_="vaticanindex")
                index_items = index.ul.find_all("li")
                if not index_items:
                    complete = True
                else:
                    for index_item in index_items:
                        whole_index.append({
                            "url": index_item.h1.a['href'],
                            "label": index_item.h1.a.string,
                        })
                    page += 1
        return whole_index

    def get_content(self, index):
        """
        :param index: [{"url": "...", "label": "..."}, ...]
        :return: [{"url": "...", "label": "...", "title": "...", "date": "...", }, ...]
        """
        whole_content = list()
        for el in index:
            url = el.get("url")
            el["date"] = datetime.strptime(url.split("_")[1], "%Y%m%d")  # We extract date from url
            el["id"] = url.split("_")[2][:-5]  # We remove .html and extract content id from url
            res = requests.get(url)
            bs = BeautifulSoup(res.content, 'html.parser')
            content = bs.find(class_="testo")
            for order, header in enumerate(content.find_all(align="center")):
                # We separate headers from rest of text
                head = header.extract()
                if order == 0:
                    el["date_title"] = get_text_from_bs(head)
                if order == 2:
                    el["context"] = get_text_from_bs(head)
                if order == 3:
                    # We try to collect youtube video url in iframe element
                    multimedia_link = head.a['href']
                    multimedia_res = requests.get(multimedia_link)
                    multimedia_bs = BeautifulSoup(multimedia_res.content, 'html.parser')
                    i_frame = multimedia_bs.find('iframe')
                    if i_frame:
                        el["multimedia"] = i_frame['src']

            el["content"] = content
            whole_content.append(el)
        return whole_content


if __name__ == '__main__':
    vs = VaticanScraper()
    content_index = vs.get_content_index(content_type="homilies")
    whole_content = vs.get_content(content_index)
    with open('./pope_homilies.json', 'wb') as f:
        import json
        json.dump(whole_content, f)