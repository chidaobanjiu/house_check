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
    with open(path, 'w', encoding='utf-8') as f:
        f.write('var districts = ')
        f.writelines(str(data))


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        # log('load', s)
        return json.loads(s)


def log(*args, **kwargs):
    print('log<{}>'.format(time.strftime("%X")), *args, **kwargs)


def path_with_query(path, query):
    pwq = path + query
    return pwq
 

def header_from_dict(headers):
    header_list = []
    for k in headers.keys():
        header_list.append('{}: {}\r\n'.format(k, headers[k]))
    hfd = ''.join(header_list)
    return hfd


def cut(data, knife):
    if knife in data:
        begin = data.split(knife)[1]
        end = begin.find('</div>')
        answer = begin[:end]
        return answer
    else:
        return 'Do not have {}'.format(knife)


def parsed_houses(body, li):
    lb = body.split('<ul class="sellListContent"')[1]
    rb = lb.split('<div class="page-box fr">')[0]
    m_list = rb.split('</li>')
    house_list = li
    for i in range(1, len(m_list) - 1):
        mv = m_list[i]
        knifes = [
            'data-el="region">',  # 信息， 例如‘和平里东街9号院 </a> | 2室1厅 | 83.08平米 | 西北 | 简装 | 有电梯’
            'target="_blank">',  # 地区，例如‘崇文门’
            '<span>单价',  # 房子单价
        ]
        house = []
        for k in knifes:
            house.append(cut(mv, k))
        log(house)
        house_list.append(house)
    return house_list


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


def parsed_message(message):
    parsed = []
    log('in', message)
    for m in message:
        log('devide', m)
        name = m[0].split('</a>')[0]
        position = m[1].split('</a>')[0]
        price = m[2].split('</span>')[0]
        parsed.append([name, position, price])
    return parsed


def list_to_dict(houses):
    dl = []
    for m in houses:
        d = dict(name = m[0], price = m[2])
        dl.append(d)
    return d


def house_path():
    path_list = []
    for i in range(1, 100):
        p = 'pg{}/'.format(i)
        path_list.append(p)
    return path_list


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
    url = 'http://bj.lianjia.com/ershoufang/'

    parsed_body = []
    path_list = house_path()
    for path in path_list:
        r = get(url, path)
        body = parsed_response(r)[2]
        parsed_body = parsed_houses(body, parsed_body)
    log('before', parsed_body)
    parsed_body = parsed_message(parsed_body)
    log(parsed_body)
    save(parsed_body, 'houses.js')
    log(len(parsed_body))


if __name__ == '__main__':
    main()
