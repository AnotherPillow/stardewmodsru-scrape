import requests, xmltodict, json
from bs4 import BeautifulSoup as bs4

CATEGORIES_XML_URL = 'https://stardewmods.ru/category_pages.xml'
CATEGORIES_XML = requests.get(CATEGORIES_XML_URL).text
CATEGORIES_JSON = xmltodict.parse(CATEGORIES_XML)
CATEGORIES_DATA = CATEGORIES_JSON['urlset']['url']

category_page0_urls = []
for item in CATEGORIES_DATA:
    print('Found category: ' + item['loc'])
    category_page0_urls.append(item['loc'])

category_pagecounts = []

for page0 in category_page0_urls:
    text = requests.get(page0).text
    soup = bs4(text, features='html.parser')
    
    pagination = soup.find("ul", class_="pagination")
    if pagination is not None:
        second_li = pagination.find_all("li")[1]
        last_a = second_li.find_all("a")[-1]

        page_count = int(last_a.text)
    else:
        # only one page
        page_count = 1

    print(f'{page0} has {page_count} page(s)')
    category_pagecounts.append([page0, page_count])

mods = {}

print('\n\n')

for category, pagecount in category_pagecounts:
    if not category.endswith('/'): category += '/'
    category_name = category.split('/')[-2]

    if category_name not in mods: mods[category_name] = []

    for pageNumber in range(1, pagecount + 1):
        print(f'getting {category} page {pageNumber}')
        url = f'{category}page/{pageNumber}/'
        text = requests.get(url).text
        catsoup = bs4(text, features='html.parser')

        containers = catsoup.select('#mains > div > div > .short')
        for container in containers:
            mod = {}

            anchor = container.select_one('.img-short > a')
            mod['preview_href'] = anchor.get('href')

            img = anchor.select_one('img')
            mod['preview_image'] = f'https://stardewmods.ru{img.get("src")}'

            title = container.select_one('.img-short > .img-short-title > a')
            mod['preview_title'] = title.get_text()

            print(f'Getting mod {title.get_text()} ({anchor.get("href")})')
            
            description = container.select_one('.short-desc')
            mod['preview_description'] = description.get_text()

            updated_date = container.select_one('.short-bott > noindex > span')
            mod['preview_updated_date'] = updated_date.get_text()

            views = container.select_one('.short-bott > noindex > a[title="Количество просмотров"]')
            mod['preview_views'] = int(views.get_text().strip().replace(" ", ""))

            fullpage = requests.get(mod['preview_href']).text
            fullsoup = bs4(fullpage, features='html.parser')

            top_outline_info = fullsoup.select_one('.customnews > .customnews-info')
            top_outline_spans = top_outline_info.select('span')
            for span in top_outline_spans:
                t = span.get_text()
                split = t.split(':')
                if len(split) == 1 or len(t) == 0: continue
                k = split[0].strip()
                v = split[1].strip()
                if k == 'Автор модификации': k = 'Author'
                if k == 'Версия мода': k = 'Version'
                if k == 'Версия перевода': k = 'TranslationVersion'
                if k == 'Дата создания публикации': k = 'DatePublished'
                if k == 'Автор перевода': k = 'TranslationAuthor'
                if k == 'Обновлено': k = 'IsUpdated'
                if k == 'Оригинал на': k = 'OriginalSite'

                mod[f'full_{k}'] = v

            description_container = fullsoup.select_one('.full-news > .customnews-info2')
            mod['full_description_html'] = str(description_container)

            images_container = description_container.select('.body_screen a')
            for i in range(len(images_container)):
                mod[f'full_extra_img_{i}'] = images_container[i].get('href')

            file_containers = description_container.select('.link_block') # possibility of multiple?
            for i in range(len(file_containers)):
                file = {}
                container = file_containers[i]

                name = container.select_one('.link_block_name')
                size = container.select_one('.link_block_download > p')
                download_anchor = container.select_one('.link_block_download > a')
                
                download_href = download_anchor.get('href')
                # download count is added to html on server
#                download_count = download_anchor.select_one('.click_counter')
                download_count = requests.get('https://stardewmods.ru/click_counter/index.php?type=get&href=' + download_href).text # if you change to to ?type=set and send a single GET request, it'll increase the counter by 

                file['name'] = name.get_text()
                file['size'] = size.get_text()
                file['href'] = download_href
                file['download_count'] = int(download_count)
#                file['download_count'] = int(download_count.get_text()) if download_count != None else '???'

                content_block = container.select_one('.link_block_content')

                date_el = content_block.select_one('.link_date_1')
                if date_el is not None:
                    date_str = date_el.get_text().split('-')[1].strip()
                    file['uploaded'] = date_str
                else:
                    file['uploaded'] = '???'

                file['description_html'] = str(content_block)

                socials = content_block.select('.link-div-block > span')
                for social in socials:
                    mod[f'author_social_{social.get_text()}'] = social.get('href')
                
                mod[f'full_file_{i}'] = file


                                                        

            mods[category_name].append(mod)

#            break

 #       break

#    break



with open('mods.json', 'w', encoding='utf-8') as f:
    json.dump(mods, f, indent=4, ensure_ascii=False)
    print('File written')

