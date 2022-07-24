from pyquery import PyQuery as pq
import httpx
import re
from config import weibo_cookies

weibo_detail_api = 'https://weibo.com/ajax/statuses/show?id='

def parse_site(msg_content):
    items = []
    if 'https://weibo.com/' in msg_content:
        urls = re.findall(r'https://weibo.com/\d+/\S+', msg_content)
        for url in urls:
            items.append(parse_weibo_url(url))
    elif 'https://mp.weixin.qq.com/s' in msg_content:
        urls = re.findall(r'https://mp\.weixin\.qq\.com/s/\S+', msg_content)
        for url in urls:
            items.append(parse_wechat_url(url))
    elif 'https://m.weibo.cn/' in msg_content:
        urls = re.findall(r'https://m.weibo.cn/\d+/\d+', msg_content) + re.findall(r'https://m.weibo.cn/status/\d+', msg_content)
        for url in urls:
            items.append(parse_weibo_m_url(url))
    elif 'https://www.jjwxc.net/onebook.php?novelid=' in msg_content:
        urls = re.findall(r'https://www\.jjwxc\.net/onebook\.php\?novelid=\d+', msg_content)
        for url in urls:
            items.append(parse_jjwxc_url(url))
    elif 'https://www.douban.com/group/topic/' in msg_content:
        urls = re.findall(r'https://www\.douban\.com/group/topic/\d+', msg_content)
        for url in urls:
            items.append(parse_douban_url(url))
    return items

def parse_weibo_m_url(url):
    html_content = httpx.get(url).text
    doc = pq(html_content)
    bid = re.search(r'\"bid\":\s\"(.*)\"', html_content).group(1)
    uid = re.search(r'\"uid\":\s(.*)', html_content).group(1)
    web_url = 'https://weibo.com/{}/{}'.format(uid, bid)
    content = pq(re.search(r'\"text\":\s\"(.*)\"', html_content).group(1)).text()
    if (len(content) > 1000):
        content = content[0:1000]+'...'
    pics = re.findall(r'\"url\":\s\"(.*)\"', html_content)
    large_pics = []
    for i in pics:
        if 'large' in i:
            large_pics.append(i)
    video_url = re.search(r'\"mp4_720p_mp4\":\s\"(.*)\"', html_content).group(1) if 'mp4_720p_mp4' in html_content else None
    return {
        'title': re.search(r'\"status_title\":\s\"(.*)\"', html_content).group(1),
        'author': re.search(r'\"screen_name\":\s\"(.*)\"', html_content).group(1),
        'author_head': re.search(r'\"profile_image_url\":\s\"(.*)\"', html_content).group(1),
        'author_url': re.search(r'\"profile_url\":\s\"(.*)\"', html_content).group(1),
        'content': content,
        'pics': large_pics,
        'video_url': video_url
    }


def parse_weibo_url(url):
    weibo_id = re.split(r'[?#]', url)[0].split('/')[-1]
    detail_url = weibo_detail_api + weibo_id
    res = httpx.get(detail_url)
    detail_json = res.json()
    pics = []
    video_url = ''
    if 'pic_infos' in detail_json:
        for pic_info in detail_json['pic_infos'].values():
            pics.append(pic_info['large']['url'])
    if 'page_info' in detail_json and 'media_info' in detail_json['page_info']:
        video_url = detail_json['page_info']['media_info']['h5_url']
    if detail_json['ok'] == 1:
        return {
            'title': '',
            'author': detail_json['user']['screen_name'],
            'head': detail_json['user']['profile_image_url'],
            'content': detail_json['text_raw'],
            'pics': pics,
            'video_url': video_url
        }
    else:
        return None


def parse_wechat_url(url):
    doc = pq(url)
    author = doc('#profileBt > a').text()
    head = list(doc('img').items())[1].attr('data-src')
    img = doc('img.rich_pages:first').attr('data-src')
    title = doc('#activity-name').text()
    content = doc('#js_content').text().replace('\n\n\n', '\n').strip()[0:500]+'...'
    return {
        'title': title,
        'author': author,
        'head': head,
        'pics': [img],
        'content': content
    }


def parse_jjwxc_url(url):
    res = httpx.get(url)
    res.encoding = 'gb2312'
    doc = pq(res.text)
    title = doc('span[itemprop=articleSection]').text()
    # title_en = translator.translate(title).text
    author = doc('span[itemprop=author]').text()
    # author_en = translator.translate(author).text
    status = doc('span[itemprop=updataStatus]').text()
    # status_en = translator.translate(status).text
    wordCount = doc('span[itemprop=wordCount]').text()
    collectedCount = doc('span[itemprop=collectedCount]').text()
    summary = doc('div[itemprop=description]').text().replace('~', '').replace('||', '|')
    # summary_en = translator.translate(summary).text.replace('~', '').replace('||', '|')
    tags = doc('div.smallreadbody>span>a').text().replace(' ', '/')
    cover = doc('img.noveldefaultimage').attr('src')
    # tags_en = translator.translate(tags).text
    return {
        # 'title': '{}({})'.format(title, title_en),
        # 'author': '{}({})'.format(author, author_en),
        # 'status': '{}/{}'.format(status, status_en),
        'title': title,
        'author': author,
        'status': status,
        'other_info': 'word count:{}\ncollected count: {}'.format(wordCount.replace('字', 'chars'), collectedCount),
        'tags': tags,
        'summary': summary,
        'cover': cover
    }

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

def parse_douban_url(url):
    res = httpx.get(url, headers=header)
    doc = pq(res.text)
    imgs = doc('.topic-doc img').items()
    pics = []
    for i in imgs:
        pics.append(i.attr('src'))
    return {
        'url': url,
        'title': doc('.article h1').text(),
        'content': doc('.topic-doc p').text(),
        'time': doc('span.create-time').text(),
        'author': doc('span.from').text(),
        'author_pfp': doc('img.pil').attr('src'),
        'pics': pics
    }

def translate_msg(msg):
    return translator.translate(msg).text

if __name__ == '__main__':
    # print(parse_weibo_m_url('https://m.weibo.cn/status/4669070841222847'))
    # print(parse_weibo_url('https://weibo.com/7509698839/LDJ78sC2M#repost'))
    print(parse_weibo_url('https://weibo.com/3947333230/KtA9KdESb'))
    # print(parse_wechat_url('https://mp.weixin.qq.com/s/YwHhX-A8tRJ37RCNHqLxdQ '))
    # print(parse_jjwxc_url('https://www.jjwxc.net/onebook.php?novelid=4472787'))
    # print(translate_msg('你好'))
    # print(parse_douban_url('https://www.douban.com/group/topic/271430038/'))
