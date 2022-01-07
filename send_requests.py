import time
import random
import argparse
import requests
import threading
from lxml.html import fromstring

argument_parser = argparse.ArgumentParser(prog='r.py')
argument_parser.add_argument('--url', dest='url', required=True)
argument_parser.add_argument('--ip-list-file', dest='ip_list_file', required=True)
argument_parser.add_argument('--min-request-times', dest='min_request_times', type=int, default=1)
argument_parser.add_argument('--max-request-times', dest='max_request_times', type=int, default=10)
argument_parser.add_argument('--min-wait', dest='min_wait', type=float, default=2)
argument_parser.add_argument('--max-wait', dest='max_wait', type=float, default=5)
argument_parser.add_argument('--thread-num', dest='thread_num', type=int, default=2)


def get_proxies():
    response = requests.get(url='https://free-proxy-list.net/')
    parser = fromstring(response.text)
    proxies = []
    for i in parser.xpath('//div[@class="table-responsive fpl-list"]/table/tbody/tr'):
        if i.xpath('.//td[7][contains(text(),"yes")]') and (i.xpath('.//td[8][contains(text(),"secs")]') or i.xpath('.//td[8][contains(text(),"min")]')):
            #Grabbing IP and corresponding PORT
            proxy_str = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.append(proxy_str)

    return proxies

def send_requests(url, request_times, min_wait, max_wait, thread_serial, ip, proxy=None):
    if proxy:
        print("Thread#" + str(thread_serial) + ": Start sending requests via proxy " + proxy + " ..., " + str(request_times) + " requests expected.")
        proxies = {'http': proxy, 'https': proxy}
    else:
        print("Thread#" + str(thread_serial) + ": Start sending requests..., " + str(request_times) + " requests expected.")

    for total_request_times in range(request_times):
        if total_request_times != 0:
            time.sleep(sleep_time)

        headers = {
                   'Cache-Control': "no-cache", 'X-Forwarded-For': ip,
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
                  }
        try:
            if proxy:
                response = requests.request("GET", url, timeout=3, proxies=proxies, headers=headers)
            else:
                response = requests.request("GET", url, timeout=3, headers=headers)

        except Exception as err:
            print('Thread#'+ str(thread_serial) + ': Request No.'+ str(total_request_times+1) + ' (using IP '+ ip +' via proxy ' + proxy + ') is FAILED!')
            sleep_time = random.uniform(min_wait, max_wait)
            continue

        msg = 'Thread#'+ str(thread_serial) +': Request No.'+ str(total_request_times+1) + ' (using IP '+ ip +' via proxy ' + proxy + ') is Done.'
        print(msg)

        if total_request_times+1 != request_times:
            sleep_time = random.uniform(min_wait, max_wait)

    print("Thread#"+str(thread_serial)+': Thread End.')


print("\nProgram start.")
args = argument_parser.parse_args()
ip_list_file = args.ip_list_file
url = args.url
min_request_times = args.min_request_times
max_request_times = args.max_request_times +1
min_wait = args.min_wait
max_wait = args.max_wait
thread_num = args.thread_num

with open(ip_list_file, 'r') as f:
    ip_list = f.readlines()

random.shuffle(ip_list)
threads = []
request_thread_made = 0
while request_thread_made < thread_num:
    print("Searching for available proxies...")
    proxies = get_proxies()
    for proxy in proxies:
        try:
            response = requests.request("GET", url, timeout=3, proxies={'http': proxy, 'https': proxy})
        except:
            print('Proxy '+ proxy + ' is NOT available.')
            continue

        else:
            print('Proxy '+ proxy + ' is available. Starting request thread#' + str(request_thread_made+1) + '...')
            ip = random.choice(ip_list).rstrip("\n")
            request_times = random.randrange(min_request_times, max_request_times)
            thread = threading.Thread(target=send_requests, args=(url, request_times, min_wait, max_wait, request_thread_made+1, ip, proxy))
            thread.start()
            threads.append(thread)
            request_thread_made += 1

            if request_thread_made >= thread_num:
                break

for thread in threads:
    thread.join()

print('Program End. Press enter to exit.')
exit()

