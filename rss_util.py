import feedparser
from pyquery import PyQuery as pq
from config import weibo_id, jike_id
import time, ssl

ssl._create_default_https_context = ssl._create_unverified_context

def parse_rss(rss_url, last_query_time):
    rss_list = feedparser.parse(rss_url)
    result_list = []
    for e in rss_list.entries:
        doc = pq(e.description)
        img_urls = []
        ttarticle_link = ''
        extra = []
        if doc('img'):
            for i in doc('img').items():
                img_urls.append(i.attr('src'))
        if doc('a'):
            for a in doc('a').items():
                href = a.attr('href')
                if 'ttarticle' in href:
                    ttarticle_link = href
                elif not ('index?extparam' in href 
                    or 'search?containerid' in href 
                    or 'weibo.com/n/' in href 
                    or 'weibo.com/p/' in href 
                    or 'huodong.weibo.cn' in href):
                    extra.append(href)
        real_time_unix = time.mktime(e.published_parsed)+8*3600
        real_show_time = time.asctime(time.localtime(real_time_unix))
        if real_time_unix > last_query_time:
            result_list.append({
                'title': e.title,
                'content': doc.text(),
                'img_urls': img_urls,
                'ttarticle_link': ttarticle_link,
                'extra': extra,
                'time': real_show_time,
                'time_unix': int(real_time_unix*1000),
                'url':e.link
            })
    return result_list


if __name__ == '__main__':
    # print(parse_rss(rss_self_list[1], time.time))
    pass