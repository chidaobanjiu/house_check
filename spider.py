import os
import json
import requests
from pyquery import PyQuery as pq
from data.data_pre.beijing_districts import districts as bj_dis
from data_generator import main as js_generater
from utils import (
    save,
    load,
    log,
)


class Model(object):
    def __repr__(self):
        name = self.__class__.__name__
        k_y = dict(self.__dict__).items()
        properties = ('{}:({})'.format(k, v) for k, v in k_y)
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class House(Model):
    def __init__(self):
        self.name = ''
        self.link = ''
        self.hot = ''
        self.type = ''
        self.info = ''
        self.unit_price = ''
        self.total_price = ''
        self.region = ''
        self.district = ''
        self.subway = ''
        self.haskey = ''
        self.taxfree = ''
        self.center = ''


def cached_url(url, filename, folder):
    path = os.path.join(folder, filename)
    log('path', path)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        if not os.path.exists(folder):
            os.makedirs(folder)

        headers = {
            'user-agent': '''
            Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/
            537.36 (KHTML, like Gecko) Chrome/
            57.0.2987.98 Safari/
            537.36Accept: text/
            html,application/
            xhtml+xml,application/
            xml;q=0.9,image/webp,*/
            *;q=0.8''',
        }

        r = requests.get(url, headers)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content


def cached_house(data, num):
    folder = 'data/json_house'
    filename = 'house_with_location_pg{}.txt'.format(num)
    path = os.path.join(folder, filename)
    log('path', path)
    if os.path.exists(path):
        return load(path)
    else:
        if not os.path.exists(folder):
            os.makedirs(folder)
        for i in range(len(data)):
            if i < 2000:
                query = 'address=北京市' + data[i]['district'] + data[i]['region'] + '&key=24182c1521603e2ab610af4a961631f4'
                url = 'http://restapi.amap.com/v3/geocode/geo?'
                request_path = url + query
                r = requests.get(request_path).content
                r = r.decode('utf-8')
                m = json.loads(r)
                log('re', m)
                info = m.get('geocodes')[0].get('location')
                data[i]['center'] = info
        save(data, path, 'w')
        log('#### position inserted ####')
        return load(path)


def cached_district(data):
    folder = 'data/json_district'
    filename = 'district_with_subdistricts.txt'
    path = os.path.join(folder, filename)
    log('path', path)
    if os.path.exists(path):
        return load(path)
    else:
        if not os.path.exists(folder):
            os.makedirs(folder)
        folder = 'data/data_pre'
        filename = 'districts.txt'
        dis_path = os.path.join(folder, filename)
        dis = load(dis_path)
        log(dis)
        for i in range(len(dis)):
            dis[i]['sub_districts'] = []
            for sb in data[i]:
                query = 'address=北京市' + dis[i]['name'] + sb + '&key=24182c1521603e2ab610af4a961631f4'
                url = 'http://restapi.amap.com/v3/geocode/geo?'
                request_path = url + query
                log('请求地区坐标：{}'.format(request_path))
                r = requests.get(request_path).content
                r = r.decode('utf-8')
                m = json.loads(r)
                info = m.get('geocodes')[0].get('location')
                dis[i]['sub_districts'].append(dict(name=sb, center=info, count=0, regions=[]))
        log(dis)
        save(dis, path, 'w')
        log('#### districts inserted ####')


def data_from_div(div, filename):
    e = pq(div)
    h = House()
    if 'pg' in filename:
        h.name = e('.title').text()
        h.link = e('.title').find('a').attr('href')
        h.hot = e('.followInfo').text()

        tad = e('.positionInfo').text().split('  - ')
        h.type = tad[0]
        h.district = tad[1]
        h.unit_price = e('.unitPrice').text()
        h.total_price = e('.totalPrice').text()

        iar = e('.houseInfo').text().split(' | ')
        h.info = iar[1]
        h.region = iar[0]
        h.follow = e('.followInfo').text()
        h.haskey = e('.haskey').text()
        h.subway = e('.subway').text()
        h.taxfree = e('.taxfree').text()

        return h.__dict__
    elif 'district' in filename:
        districts = []
        sub = e('a').text().split(' ')
        j = 0
        for i in range(len(sub)):
            if sub[i] == '1号线':
                j = i
        return sub[20:j]


def data_from_url(url, filename, folder):
    log('url for {}: {}'.format(filename, url))
    page = cached_url(url, filename, folder)
    e = pq(page)
    if 'pg' in filename:
        e = e('.sellListContent')
        items = e('.info')
        datas = [data_from_div(i, filename) for i in items]
        return datas
    elif 'district' in filename:
        e = e('.m-filter')
        datas = data_from_div(e, filename)
        return datas


def main():
    houses = []
    districts = []
    # 获取链家二手房1-100页的信息
    for i in range(1, 101):
        url = 'http://bj.lianjia.com/ershoufang/pg{}/'.format(i)
        folder = 'cached/house'
        filename = 'pg' + url.split('pg')[1].replace('/', '') + '.html'
        house = data_from_url(url, filename, folder)
        houses.extend(house)
        # 将获取的所有数据分成 25 50 75 100 四个部分进行数据缓存，以备之后的进一步处理
        if i in (25, 50, 75, 100):
            log('#### total houses: {} ####'.format(len(houses)))
            houses = cached_house(houses, i)
            houses = []
    # 爬取行政区划与地理区域的划分
    for d in bj_dis:
        url = 'http://bj.lianjia.com/ershoufang/{}/'.format(d)
        folder = 'cached/district'
        filename = 'district-' + url.split('/')[4] + '.html'
        district = data_from_url(url, filename, folder)
        districts.append(district)
    cached_district(districts)
    log('####     districts and houses data ready    ####')
    log('#### districts data in <data/json_district> ####')
    log('####     houses data in <data/json_house>   ####')


if __name__ == '__main__':
    main()
    js_generater()

# &plugin=AMap.DistrictSearch