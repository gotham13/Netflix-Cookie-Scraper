"""
Created by Gotham on 7/6/2019.
"""
import bs4 as bs
import requests
import re
import time
import json
import base64
import os
import shutil
import multiprocessing
import itertools
import threading
import sys

sauce = requests.get('https://tecknity.com/free-netflix-account-cookies/')
soup = bs.BeautifulSoup(sauce.content, 'lxml')
all_a = soup.findAll('a', {'class': 'maxbutton-19 maxbutton maxbutton-new-netflix-cookie goToCookien'})
ids = list(map(lambda e: e['href'].replace("javascript:en_url_new('", '').replace("')", ''), all_a))

type = None
url = None
scripts = soup.findAll('script')
for script in scripts:
    tpe = re.findall(r'var type = (.*?);',str(script.string))
    if len(tpe) == 2:
        type = tpe[1].strip('"')
        url = re.findall(r'var url = (.*?);', str(script.string))[1].strip("'")
        break


def en_url(key):
    secs = str(round(time.time()))
    ps1 = key[0:2]
    ps2 = key[2:4]
    ps3 = key[4:6]
    pt1 = secs[0:3]
    pt2 = secs[3:6]
    pt3 = secs[6:9]
    pt4 = secs[len(secs)-1]
    data = pt3 + ps1 + pt2 + ps2 + pt4 + type + ps3 + pt1
    return data


headers = {
    'origin': "https://tecknity.com",
    'upgrade-insecure-requests': "1",
    'cache-control': "no-cache",
    'content-type': "application/x-www-form-urlencoded",
}

countries = ['IN', 'US', 'KP']


def clean_up():
    dont_remove = ['cookie_scraper.py', '.idea', '.git','requirements.txt']
    for f in os.listdir(os.getcwd()):
        if f not in dont_remove:
            print('Removing Dir {}'.format(f))
            shutil.rmtree(os.path.join(os.getcwd(), f))


def create_dirs(ccs):
    for cc in ccs:
        print('Creating dir {}'.format(cc))
        os.mkdir(os.path.join(os.getcwd(), cc))


def scraper(id1):
    for cc in countries:
        sauce1 = requests.request("POST", "https://tecknity.com" + url, data={"data": en_url(id1)}, headers=headers)
        soup1 = bs.BeautifulSoup(sauce1.content, 'lxml')
        scripts1 = soup1.findAll('script')
        data = None
        for script1 in scripts1:
            d1 = re.findall(r'var data = (.*?);', str(script1.string))
            if len(d1) == 1:
                data = d1[0].strip('"')
                break
        sauce2 = requests.request("POST", "https://tecknity.com/top-10-wordpress-hosting-services/",
                                  data={"cc": base64.b64encode(cc.encode('utf-8')).decode('utf-8'), "data": data},
                                  headers=headers)
        soup2 = bs.BeautifulSoup(sauce2.content, 'lxml')
        cookie = soup2.find('div', {'id': 'cookie_container'})
        cookie_json = json.loads(cookie.text)
        secure_data4 = cookie_json['cookie']['SecureData4']
        acc_id = base64.b64decode(secure_data4).decode("utf-8")
        cookie_dir = os.path.join(os.getcwd(), cc)
        cookie_name = acc_id.split('@')[0]+'.html'
        if acc_id == 'nulled@thetechstuff.in':
            continue
        with open(os.path.join(cookie_dir, cookie_name), 'w') as file:
            file.write(sauce2.text)


done = False


def animate():
    init_time = time.time()
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rFetching Cookies ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')
    final_time = time.time()
    sys.stdout.write('Total time taken = {} seconds'.format(round(final_time - init_time)))


if __name__ == '__main__':
    clean_up()
    create_dirs(countries)
    t = threading.Thread(target=animate)
    t.start()
    pool = multiprocessing.Pool(processes=10)
    pool.map(scraper, ids)
    pool.close()
    pool.join()
    done = True
