import ssl, socket, time, json

'''
def save(data, path):
    """
    data 是 dict 或者 list
    path 是保存文件的路径
    """
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8') as f:
        # log('save', path, s, data)
        f.write(s)
'''


def save(data, path):
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8') as f:
        # log('save', path, s, data)
        f.write(s)


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        # log('load', s)
        return json.loads(s)


def load_body(body):
    log('load', body)
    return json.loads(body)

def log(*args, **kwargs):
    print('log<{}>'.format(time.strftime("%X")), *args, **kwargs)


def path_with_query(path, query):
    names = []
    for k in query.keys():
        names.append('{}={}'.format(k, query[k]))
    pwq = path + '?' + '&'.join(names)
    return pwq


def parsed_url(url):
    protocol = 'http'
    if 'https://' in url:
        protocol = 'https'
        u = url.split('//')[1]
    elif 'http://' in url:
        u = url.split('//')[1]
    else:
        u = url

    j = u.find('/')
    if j == -1:
        path = '/'
        host = u
    else:
        host = u[:j]
        path = u[j:]

    if ':' in host:
        h = host.split(':')
        host = h[0]
        port = int(h[1])
    else:
        if protocol == 'http':
            port = 80
        else:
            port = 443

    return protocol, host, port, path


def get_response(s):
    buffer_size = 10240
    response_bytes = b''
    while True:
        response = s.recv(buffer_size)
        if len(response) == 0:
            break
        response_bytes += response
    return response_bytes


def get_protocol(protocol):
    s = socket.socket()
    if protocol == 'https':
        s = ssl.wrap_socket(socket.socket())
    return s


def parsed_response(response):
    res = response.decode('utf-8', 'ignore')
    header, body = res.split('\r\n\r\n', 1)
    heads = header.split('\r\n')
    status_code = heads[0].split()[1]
    status_code = int(status_code)
    headers = {}
    for head in heads[1:]:
        k, v = head.split(': ')
        headers[k] = v
    return status_code, headers, body


def list_to_dict(houses):
    dl = []
    for m in houses:
        d = dict(address='北京' + m[0], key='24182c1521603e2ab610af4a961631f4')
        dl.append(d)
    return dl


def get_pos(body):
    b = load_body(body)
    pos = b['geocodes']
    return pos



def get(url, query):
    protocol, host, port, path = parsed_url(url)
    s = get_protocol(protocol)
    port = int(port)
    path = path_with_query(path, query)
    log(host, port)
    s.connect((host, port))
    log(host + path)
    http_request = 'GET {} HTTP/1.1\r\nHost:{}\r\nConnection:close\r\n\r\n'.format(path, host)
    request = http_request.encode('utf-8')
    s.send(request)
    response = get_response(s)
    status_code, headers, body = parsed_response(response)
    if status_code in [301, 302]:
        return get(headers['Location'], query)
    return response


def main():
    url = 'http://restapi.amap.com/v3/geocode/geo'

    house = load('houses.txt')
    path_list = list_to_dict(house)
    log('path_list', path_list)
    get_message = []
    for i in range(1000):
        log('i=', i)
        log('pathlist', path_list[i])
        r = get(url, path_list[i])
        body = parsed_response(r)[2]
        log('body', body)
        get_message.append(body)
        pos = get_pos(body)
        house[i].append(pos)
    save(house, 'housewithlocation{}.txt'.format(i))
    save(get_message, 'get_message{}.txt'.format(i))
    log('last answer', house)
    save(get_message, 'get_message.txt')
    log(len(house))


if __name__ == '__main__':
    main()
'''
l = load('housewithlocation999.txt')
log(l)
data = []
for i in range(1000):
    l[i][0] = {}
    dic = l[i][0]
    dic['name'] = l[i][0]
    dic['street'] = l[i][1]
    dic['price'] = l[i][2]
    dic['district'] = l[i][3][0]['district']
    dic['location'] = l[i][3][0]['location']
    dic['formatted_address'] = l[i][3][0]['formatted_address']
    data.append(dic)
save(data, 'houses.txt')
'''



'''
{'count': '1',
 'info': 'OK',
 'geocodes': [
     {
         'location': '116.255967,39.905658',
         'province': '北京市',
         'neighborhood': {
             'type': [],
             'name': []
         },
         'formatted_address': '北京市海淀区铁建大院',
         'citycode': '010',
         'street': [],
         'number': [],
         'adcode': '110108',
         'district': '海淀区',
         'level': '兴趣点',
         'building': {
             'type': [],
             'name': []
         },
         'city': '北京市',
         'township': []
    }
 ],
 'infocode': '10000',
 'status': '1'
 }
'''