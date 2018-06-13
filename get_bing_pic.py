import requests
import os
from bs4 import BeautifulSoup
import re
from set_wallpaper import set_wallpaper

HOMEPAGE_URL = 'http://cn.bing.com/'
JSON_URL = HOMEPAGE_URL + 'HPImageArchive.aspx'
TEXT_URL = HOMEPAGE_URL + 'cnhp/life'
AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36 OPR/52.0.2871.99'
HEADERS = {
    'User-Agent' :  AGENT,
    'Accept-Language' : 'zh-CN,zh;q=0.9',
    'referer' : HOMEPAGE_URL}

def get_resource(url, headers, params):
    try:
        r = requests.get(url, headers = headers, params = params)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        #print('URL: ' + r.url)
    except Exception as e:
        print(e)
        r = None
    finally:
        return r
    
def set_json_params(params, n):
    params['format'] = 'js'
    params['idx'] = 0
    params['n'] = n

def get_pic_info(json):
    pic_list = []
    try:
        for image in json['images']:
            print("{enddate} {copyright} {url}".format(**image))
            info = {}
            info['enddate'] = image['enddate']
            info['copyright'] = image['copyright']
            info['url'] = image['url']
            pic_list.append(info)
    except Exception as e:
        print(e)
    return pic_list

def save_file(content, path):
    with open(path, 'wb') as f:
        f.write(content)
        print('Save file: ' + path)
        
def save_file_from_url(url, path):
    with open(path, 'wb') as f:
        r = get_resource(url, HEADERS, None)
        f.write(r.content)
        print('Save file: ' + path)
        
def mkdir(path):
    path = path.strip().rstrip(os.path.sep)
    if not os.path.exists(path):
        os.makedirs(path) 
        return True
    else:
        return False
    
def get_text(date):
    params = {}
    params['currentDate'] = date
    params['ensearch'] = 0
    r = get_resource(TEXT_URL, HEADERS, params)
    soup = BeautifulSoup(r.text, 'html.parser')
    pic_title0 = soup.select('.hplaAttr')[0].text
    pic_title1 = soup.select('.hplaTtl')[0].text
    text_title0 = soup.select('.hplatt')[0].text
    text_title1 = soup.select('.hplats')[0].text
    snippet = soup.select('#hplaSnippet')[0].text
    writer = soup.select('.hplaPvd')[0].text
    tplt = '{0}: {1}{ls}{2}{ls}{3}{ls}{4}{ls}{5}'
    text = tplt.format(pic_title0, pic_title1, text_title0, text_title1, snippet, writer, ls=os.linesep)
    print(text)
    return text
  
def main():
    params = {}
    n = input('获取最近几天的Bing每日一图(1~8)：') or '1'
    set_json_params(params, int(n))
    r = get_resource(JSON_URL, HEADERS, params)
    pic_list = get_pic_info(r.json())
    mkdir('bing_pic')
    text_name_pattren = re.compile(r'[^/_]+_[^_]+')
    for pic in pic_list:
        pic_url = HOMEPAGE_URL + pic['url']
        pic_name = pic['url'].split('/')[-1]
        pic_path = '.' + os.path.sep + 'bing_pic' + os.path.sep + pic_name
        save_file_from_url(pic_url, pic_path)

        text = pic_name + os.linesep + pic['copyright'] + os.linesep + get_text(pic['enddate'])
        text_name = text_name_pattren.search(pic['url']).group(0) + '.txt'
        text_path = '.' + os.path.sep + 'bing_pic' + os.path.sep + text_name
        save_file(bytes(text, encoding = "utf8"), text_path)
        
        if pic is pic_list[0]:
            set_wallpaper(pic_path)

main()