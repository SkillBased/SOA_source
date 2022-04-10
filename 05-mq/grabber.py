from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

def scan_from_to(orig, dest, max_depth=8):
    fcut = orig.find(".org")
    filter_ = orig[:fcut] + ".org"
    print(f" [x] searching only on {filter_}", flush=True)
    used_links = [orig]
    queue = [[orig, 0]]
    qid = 0
    while (qid < len(queue)):
        curlink, dist = queue[qid]
        next_links = list_links(curlink)
        for link in next_links:
            real_link = link
            if real_link[:5] == "/wiki":
                real_link = filter_ + real_link
            if (real_link == dest):
                return (dist + 1)
            if (real_link.find(filter_) != -1 and real_link not in used_links and dist < max_depth):
                queue.append([real_link, dist + 1])
        qid += 1
    return -1

def list_links(page_url):
    html_page = urlopen(page_url)
    soup = BeautifulSoup(html_page, "lxml")
    links = []
    for link in soup.findAll('a', attrs={'href': re.compile("wiki/")}):
        links.append(link.get('href'))
    return links
