import httpx
from selectolax.parser import HTMLParser
import csv
from fake_useragent import UserAgent
from tqdm import tqdm

url = 'https://parsinger.ru/html/index1_page_1.html'


def get_response(link: str) -> str:
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    try:
        return httpx.get(url=link, headers=headers).text
    except httpx.HTTPError as exc:
        raise f'Something went wrong! f{exc}'


def get_html_obj(link: str) -> HTMLParser:
    return HTMLParser(get_response(link))


def get_nav_menu_links(link: str) -> list:
    """we get a link in the navigation menu"""
    html_obj = get_html_obj(link)
    try:
        return [item.attributes['href'].strip() for item in html_obj.css('div.nav_menu > a')]
    except AttributeError:
        raise f'No attribute!. Look in the inspector f{link}'


def get_link_pages(link: str) -> list:
    """we get a link to the site page"""
    html_obj = get_html_obj(link)
    try:
        return [item.attributes['href'].strip() for item in html_obj.css('div.nav_menu > a')]
    except AttributeError:
        raise f'No attribute!. Look in the inspector f{link}'


def get_item_link(link: str) -> list:
    """we get the product link to go inside the product"""
    html_obj = get_html_obj(link)
    try:
        return [item.attributes['href'].strip() for item in html_obj.css('.img_box > a.name_item')]
    except AttributeError:
        raise f'No attribute!. Look in the inspector f{link}'


def get_product_content(link) -> list:
    """
    we collect data about the product and write it down in a list
    handles each event if the data is not present it will be replaced otherwise an exception will be thrown
    """
    product_data = []
    html_obj = get_html_obj(link)
    try:
        try:
            product_name = html_obj.css_first('p#p_header').text().strip()
            if product_name:
                product_data += [product_name]
            else:
                product_data += ['No name']
        except AttributeError:
            raise 'Product name error!'
        try:
            article = html_obj.css_first('p.article').text().split(':')[1].strip()
            if article:
                product_data += [article]
            else:
                product_data += ['No article']
        except AttributeError:
            raise 'Article name error!'

        try:
            product_brand = html_obj.css_first('li#brand').text().split(':')[1].strip()
            if product_brand:
                product_data += [product_brand]
            else:
                product_data += ['No brand']
        except AttributeError:
            raise 'Brand name error!'

        try:
            product_model = html_obj.css_first('li#model').text().split(':')[1].strip()
            if product_model:
                product_data += [product_model]
            else:
                product_data += ['No model']
        except AttributeError:
            raise 'Brand name error!'
        try:
            in_stock = html_obj.css_first('span#in_stock').text().split(':')[1].strip()
            if in_stock:
                product_data += [in_stock]
            else:
                product_data += ['No stock']
        except AttributeError:
            raise 'Stock name error!'
        try:
            product_price = html_obj.css_first('span#price').text().strip()
            if product_price:
                product_data += [product_price]
            else:
                product_data += ['No price']
        except AttributeError:
            raise 'Price name error!'
        try:
            product_old_price = html_obj.css_first('span#old_price').text().strip()
            if product_old_price:
                product_data += [product_old_price]
            else:
                product_data += ['No old price']
        except AttributeError:
            raise 'Price name error!'
    except AttributeError:
        raise f'No attribute!. Look in the inspector f{link}'
    product_data += [link]
    return product_data


def makes_headlines() -> None:
    with open('date.csv', 'w', encoding='utf-8', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=';')
        writer.writerow(['Наименование', 'Артикул', 'Бренд', 'Модель', 'Наличие', 'Цена', 'Старая цена', 'Ссылка'])


def adding_product(lst: list) -> None:
    with open('date.csv', 'a', encoding='utf-8', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=';')
        writer.writerow(lst)


def processing_products(link):
    """
    a function that bypasses all pages of the site, goes to each of them and takes information,
    after that writes to csv file.
    """
    website_url = 'https://parsinger.ru/html/'
    makes_headlines()
    for nav in tqdm(get_nav_menu_links(link), desc='Collecting data from product cards...'):  # category link
        for page in get_link_pages(website_url + nav):  # category pages
            for item in get_item_link(website_url + page):  # product page
                adding_product(get_product_content(website_url + item))


# run
if __name__ == "__main__":
    print(processing_products(url))
