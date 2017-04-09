import json
import time, os


# 自定义log
def log(*args, **kwargs):
    print('log<{}>'.format(time.strftime("%X")), *args, **kwargs)


# 将数据保存为.js脚本格式 ， 可以直接在html引用
def save_js(data, path, name):
    data = 'var {} = '.format(name) + str(data)
    with open(path, 'w+', encoding='utf-8') as f:
        # log('save', path, s, data)
        f.write(data)


# 将数据保存为json格式
def save(data, path, method):
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, method, encoding='utf-8') as f:
        # log('save', path, s, data)
        f.write(s)


# 载入json格式的文件
def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        # log('load', s)
        return json.loads(s)


# 参数分别是要分割的数据 ，分割的开始，分割的结束。
def cut(data, knife, end):
    if knife in data:
        begin = data.split(knife)[1]
        end = begin.find(end)
        answer = begin[:end]
        return answer
    else:
        return 'Do not have {}'.format(knife)


def list_to_dict(houses):
    dl = []
    for m in houses:
        d = dict(name=m[0], price=m[2])
        dl.append(d)
    return dl


def dic_adjust(path, f, t):
    data = load(path)
    for d in data:
        print(d)
        value = d.get(f)
        d.pop(f)
        d[t] = value
    save(data, path, 'w')

# filename = 'json_house/house_with_location_pg100.txt'
# folder = 'data'
# path = os.path.join(folder, filename)
# dic_adjust(path, 'location', 'center')
