import json
import time


def save(data, path, name):
    data = 'var {} = '.format(name) + str(data)
    with open(path, 'w+', encoding='utf-8') as f:
        # log('save', path, s, data)
        f.write(data)


def save_json(data, path):
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8')as f:
        f.write(s)


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        # log('load', s)
        return json.loads(s)


def load_js(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def log(*args, **kwargs):
    print('log<{}>'.format(time.strftime("%X")), *args, **kwargs)


def trans(path):
    data = load(path)
    log('data', type(data))
    for h in data:
        h['price'] = h['price'][:-4]
    save(data, 'houses_.js')
    save_json(data, 'houses_.txt')


def cut(data, knife):
    if knife in data:
        begin = data.split(knife)[1]
        end = begin.find('</div>')
        answer = begin[:end]
        return answer
    else:
        return 'Do not have {}'.format(knife)


def to_dis(data, cut):
    di = data.split('subDistricts')[1]
    return di.split('{}'.format(cut))


def dis_name(data):
    name = []
    for i in data:
        ds = i.split('区')[0]
        if len(ds) < 4:
            name.append(ds)
        else:
            ds = ds.split('县')[0]
            name.append(ds)
    return name


def dis_center(data):
    center = []
    for i in data:
        ds = i.split('"')[0]
        center.append(ds)
    return center


def data_process():
    houses = load('houses_.txt')
    districts = load('Rules/districts.txt')

    for d in districts:
        k = list(d.keys())[0]
        d[k] = []
        d['houses'] = []
        d['name'] = k
        del d[k]
        for h in houses:
            dis = h['district'][:-1]
            if not dis:
                houses.remove(h)
                continue
            if dis == d['name']:
                d['houses'].append(h)

    dis_position = {}
    position = load_js('marker2.js')
    ds = to_dis(position, 'name": "')
    name = dis_name(ds)[1:]
    ds = to_dis(position, '"center": "')
    center = dis_center(ds)[1:]
    for i in range(len(name)):
        dis_position[name[i]] = center[i]

    for k in dis_position.keys():
        for d in districts:
            if k == d['name']:
                d['location'] = dis_position[k]

    save(districts, 'my_data.js', 'districts')

data_process()

