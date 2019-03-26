# coding=utf8


import requests, vk, json, random, time
from bs4 import BeautifulSoup


def get_html(status):
    """Получаем html с гипермол"""
    cookies = {'PHPSESSID': '10ugkgduggfsk51eh0ddm6o793', 'euroopt_enable': '0', '_product_unsaved': 'false'}
    cookies_evro = {'PHPSESSID': 'bscnk3jcb5cd0i2sm12ov30un7', 'euroopt_enable': '0', '_product_unsaved': 'false'}

    headers = {
        'cache-control': 'no-store, no-cache, must-revalidate',
        'content-type': 'text/html; charset=utf-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'upgrade-insecure-requests': '1',

    }

    session = requests.Session()
    if status == 'giper':
        req = session.get('https://gipermall.by/cabinet/favorites/', cookies=cookies, headers=headers)

        return req.text

    elif status == 'evro':
        req = session.get('https://gipermall.by/cabinet/favorites/', cookies=cookies_evro, headers=headers)

        return req.text

def actual_data(html):
    soup = BeautifulSoup(html, "html.parser")
    # print(soup.prettify())

    value = {}

    test = soup.find_all('div', class_='products_card')
    for i in test:
        status = i.find('button', type="submit")
        if status != None:
            prodyct_name = i.find('div', class_='title').text
            data = str(prodyct_name).split('.,')
            value.update({data[0]: 1})
        else:
            prodyct_name = i.find('div', class_='title').text
            data = str(prodyct_name).split('.,')
            value.update({data[0]: 0})

    return value


def vk_api(status='get', value='Заглушка'):
    with open('tokken.txt', 'r') as file:
        tokken = file.read()

    session1 = vk.AuthSession(
        access_token=tokken,
        scope='messages')
    vk_api = vk.API(session1, v=5.62)

    if status == 'get':

        def proverka(messages):

            for i in messages:
                id = int(i.get('message').get('user_id'))
                if id == 4010754:
                    return i.get('unread')

        messages = vk_api.messages.getDialogs(count=20, unread=1)
        status = messages.get('items')
        count = proverka(status)

        if count != None:  # Проверка на наличие Новых сообщений, если их нет то история не выгружается.
            history = vk_api.messages.getHistory(count=count, user_id='4010754', peer_id='4010754')
            messages1 = history.get('items')

            value = []
            for i in messages1:
                value.append(i.get('body'))

            # Отметить как прочитанно!
            vk_api.messages.markAsRead(peer_id='4010754')

            return value

        else:
            return []

    elif status == 'post':

        for i in value:
            vk_api.messages.send(user_id='4010754', peer_id='4010754', message=i, random_id=random.randint(1, 10000))
            time.sleep(2)

    elif status == 'user':
        vk_api.messages.send(user_id='4010754', peer_id='4010754', message=value, random_id=random.randint(1, 10000))


def file_menu(flag, value=None):
    if flag == 'r':
        with open('old.json', 'r', encoding="utf-8") as file:
            data = json.load(file)

        return data

    elif flag == 'w':
        with open('old.json', 'w', encoding="utf-8") as file:
            json.dump(value, file)


def user_data(flag, value=None):
    if flag == 'r':
        with open('userdata.txt', 'r') as file:
            value = file.read().split(',')
        return value

    elif flag == 'w':
        with open('userdata.txt', 'w') as file:
            file.write(value)


class Mainloop():
    def __init__(self, value, table, user, old):

        # dict
        self.data = value  # Актуальные данные о товарах.
        # list
        self.table = table  # Название позиций за которым нужно следить.
        # list
        self.user = user  # Данные полученные из лички вк.
        # dict
        self.oldshop = old  # Данный прошлого запуска (словарь с состояниями)

    def reaction(self):
        for i in self.user:

            if 'всё' in i:
                item_list = []
                value = ''
                nums = 0
                for name in self.data:
                    if nums != 11:
                        data = f'{name}\n'
                        a = ''.join(data)
                        value += a
                        nums += 1

                    else:
                        item_list.append(value)
                        value = ''
                        nums = 0
                        data = f'{name}\n'
                        a = ''.join(data)
                        value += a
                        nums += 1
                vk_api('user', 'Всё что я вижу в избранном')
                vk_api('post', item_list)  # Отправялем полный список того что в избранном. (ключи)

            elif 'список' in i:
                strika = ''
                for i in self.table:
                    data = f'{i}\n'
                    strika += data

                vk_api('user', 'В списке отслеживаемых товаров:')
                vk_api('user', strika)

            else:

                def fav_data(value, data):
                    for i in data:
                        if value in i:
                            return True

                    return False

                if i[0] == '+':
                    stroka = i.split('+')
                    proverka = fav_data(stroka[1], self.data)
                    if proverka == True:

                        if stroka[1] not in self.table:

                            self.table.append(stroka[1])
                            zapis = ','.join(self.table)
                            user_data('w', value=zapis)

                            vk_api('user', f'{stroka[1]} | Записал')
                        else:
                            vk_api('user', f'{stroka[1]} | Уже есть в списке отслеживания')

                    else:
                        vk_api('user', f'{stroka[1]} | Название не было найдено в избранном')

                elif i[0] == '-':
                    stroka = i.split('-')

                    def _filter(spisok, stroka):
                        # import pdb
                        # pdb.set_trace()
                        for i in spisok:
                            if stroka in i:
                                return True

                    if _filter(self.table, stroka[1]) == True:
                        for p in self.table:
                            if stroka[1] in p:
                                self.table.remove(p)
                                zapis = ','.join(self.table)
                                user_data('w', value=zapis)
                                vk_api('user', f'{stroka[1]} | Из списка отслеживания удалил!')
                    else:
                        vk_api('user', f'{stroka[1]} | НЕ УДАЛИЛ! Потому что не нашел в свписке отслеживания.')
                else:
                    vk_api('user', f'{i} | Неверная команда')

    def working(self):
        def key_cllect(new, data):
            kluchi = new.keys()
            for i in kluchi:
                if data in i:
                    return i
            return False

        old_dat = self.oldshop
        new_data = self.data
        data_user = self.table

        for x in data_user:

            data = key_cllect(new_data, x)
            if data != False:
                if old_dat.get(data) != new_data.get(data):
                    if old_dat.get(data) == 0:
                        vk_api('user', f'{data} | В НАЛИЧИИ')
                    elif old_dat.get(data) == 1:
                        vk_api('user', f'{data} | Теперь НЕ в наличии.')


def main():
    # 1 - Обработка входных данных из вк | 2 - Сравнение вводных данных с данными которые уже есть
    # 3 - Добавить новые данные (если их нет) | 4 - Сверить текущие состояние Отслеживаемых товаров с прошлым запуском
    # 5 - Вывести в вк найденные изменения | 6 - Записать новое состояние в файл json

    giper = get_html('giper')
    evrik = get_html('evro')

    value = {}
    value.update(actual_data(giper))
    value.update(actual_data(evrik))

    table = user_data('r')  # Позиции за котоырми следить.
    vk_data = vk_api()  # История сообщений из вк. (новых)

    old_data = file_menu('r')

    loop = Mainloop(value, table, vk_data, old_data)
    loop.reaction()
    loop.working()

    file_menu('w', value)


if __name__ == '__main__':
    main()
