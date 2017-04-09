import os
import json
import requests
from pyquery import PyQuery as pq
from utils import (
    save,
    save_js,
    load,
    log,
)


def to_one(paths, filename):
    houses = []
    house_folder = 'data/json_house'
    for path in paths:
        houses.extend(load(path))
    log('#### total houses in {}: {} ####'.format(filename, len(houses)))
    path = os.path.join(house_folder, filename)
    if os.path.exists(path):
        print('{} has exsit'.format(path))
        return load(path)
    else:
        save(houses, path, 'w')


def unit_price_to_region_count(r):
    prices = 0
    if r['houses'] == []:
        return 0
    else:
        for h in r['houses']:
            s = h['unit_price']
            j = 0
            q = 0
            if '单价' in s:
                for i in range(len(s)):
                    if s[i] == '价':
                        j = i
                    elif s[i] == '元':
                        q = i
            n = s[j+1:q]
            prices += int(n)
        price = prices//len(r['houses'])
        return price


def count(sub_counts):
    prices = 0
    counts = len(sub_counts)
    if sub_counts == []:
        return 0
    else:
        for r in sub_counts:
            if r['count'] == 0:
                counts -= 1
            prices += r['count']
        if prices == counts == 0:
            return 0
        else:
            price = prices//counts
            return price


def region_insert(regions, house, sub_district):
    rgs = regions
    h = house
    sd = sub_district

    if rgs == []:
        new_r = dict(name=h['region'], center=h['center'], houses=[])
        rgs.append(new_r)
    else:
        for i in range(len(rgs)):
            if h['region'] == rgs[i]['name']:
                log('{} 添加小区 {}'.format(sd['name'], h['region']))
                rgs[i]['houses'].append(h)
                break
            elif i == len(rgs) - 1 and h['region'] != rgs[i]['name']:
                new_r = dict(name=h['region'], center=h['center'], houses=[])
                rgs.append(new_r)
                log('{} 添加小区 {}'.format(sd['name'], h['region']))
                new_r['houses'].append(h)
                break
            else:
                continue


def houses_insert(house_file, dis_file):
    new_dis = os.path.join('data/json_district', '_districts_.txt')
    js_dis = os.path.join('data', 'my_data.js')

    if os.path.exists(new_dis) and os.path.exists(js_dis):
        pass
    else:
        dis_folder = 'data/json_district'
        hou_folder = 'data/json_house'
        house_path = os.path.join(hou_folder, house_file)
        dis_path = os.path.join(dis_folder, dis_file)
        districts = load(dis_path)
        houses = load(house_path)
        log('total houses:', len(houses))
        for d in districts:
            log('district:', d['name'])
            for sd in d['sub_districts']:
                rgs = sd['regions']
                log('sub_district', sd['name'])
                for h in houses:
                    if h['district'] == sd['name']:
                        log('匹配')
                        region_insert(rgs, h, sd)
                    else:
                        continue
                for r in sd['regions']:
                    r['count'] = unit_price_to_region_count(r)
                sd['count'] = count(sd['regions'])
            d['count'] = count(d['sub_districts'])

        save(districts, new_dis, 'w')
        save_js(districts, js_dis, 'districts')
        return districts, houses


def main():
    paths = []
    for num in (25, 50, 75, 100):
        json_path = 'data/json_house/house_with_location_pg{}.txt'.format(num)
        paths.append(json_path)
    filename = 'houses.txt'
    to_one(paths, filename)
    houses_insert('houses.txt', 'district_with_subdistricts.txt')


if __name__ == '__main__':
    main()

