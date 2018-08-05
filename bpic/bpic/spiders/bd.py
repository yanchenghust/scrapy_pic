# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
import MySQLdb
import json
import time
import hashlib
import logging
import re
import base64
import urllib2

logging.basicConfig(filename="/root/work/python/scrapy_error.log", level=logging.DEBUG)

# splash lua script
lua_script = """
        function main(splash, args)
            splash:go(args.url)
            splash:wait(args.load_wait)
            splash:runjs(string.format("document.querySelector('#kw').value = '%s';", args.kwname))
            splash:runjs("document.querySelector('.s_btn_wr>input').click();")
            splash:wait(args.render_wait)
            for i=1,args.page_num do
                splash:runjs("document.body.scrollTop=100000")
                splash:wait(args.render_wait)
            end
            return splash:html()
        end
        """
class BdSpider(scrapy.Spider):
    name = 'bd'
    allowed_domains = ['image.baidu.com']
    url = 'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=index&fr=&hs=0&xthttps=111111&sf=1&fmq=&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%E6%97%A5%E6%9C%AC%E5%A5%B3%E4%BC%98'
    db = MySQLdb.connect("127.0.0.1", "pic123", "pic123", "pics", charset='utf8')

    # start request
    def start_requests(self):
        for keyword in self.get_keywords():
            args = {
                'lua_source': lua_script,
                'kwname': keyword,
                'load_wait': 2,  # 页面加载秒数
                'render_wait': 3,  # 每次到达页面底部触发加载，等待渲染的秒数
                'page_num': 3,  # 页数
                'timeout': 3600,  # splash 504
            }
            logging.info("keyword: {} begin".format(keyword.encode("utf-8")))
            yield SplashRequest(self.url, callback=self.parse, endpoint='execute', meta={"keyword": keyword}, args=args)

    # parse the html content
    def parse(self, response):
        infos = response.css('img.main_img').xpath('@src').extract()
        keyword = response.meta["keyword"]
        logging.info("keyword: {} parse, pic_len: {}".format(keyword.encode("utf-8"), len(infos)))
        if len(infos) == 0:
            logging.error("parse error, resp: {}".format(response))
            return
        for pic in infos:
            self.save(pic, keyword)

    def combination(self, idx, item, lst, keywords, keys):
        if idx == len(keys):
            lst.append(item)
            return False
        if len(item) == 3:
            lst.append(item)
            return True
        for k in keywords[keys[idx]]:
            new_item = item[:]
            if k != "":
                new_item.append(k)
            if self.combination(idx + 1, new_item, lst, keywords, keys):
                break

    def get_keywords(self):
        data = json.load(open("label/label.json", "r"))
        keys = data["keys"]
        keywords = data["labels"]
        lst = []
        self.combination(0, [], lst, keywords, keys)
        for item in lst:
            # item = map(lambda x: x.encode('utf-8'), item)
            yield " ".join(item)

    def save(self, pic, keyword):
        now = time.time()
        uri_md5 = hashlib.md5()
        uri_md5.update(str(round(now * 1000)))
        uri_md5.update(pic)
        uri = uri_md5.hexdigest()
        match_obj = re.match(r'^data', pic, re.M | re.I)
        if match_obj:
            file_data = base64.b64decode(pic)
            pic = ""
        else:
            f = urllib2.urlopen(pic)
            file_data = f.read()

        cursor = self.db.cursor()
        tags = keyword.split(" ")
        tag = ",".join(tags)

        source_url_md5 = hashlib.md5()
        source_url_md5.update(pic)
        # SQL 插入语句
        sql = """insert into pics(title, extra, uri, source_url, source_url_md5, create_time, update_time, status, tag)
                 values('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
              """.format(
            "", "[]", uri, pic, source_url_md5.hexdigest(), int(now), int(now), 0, tag.encode('utf-8'), int(now)
        )
        try:
            # 执行sql语句
            # logging.info("execute sql: {}".format(sql))
            cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
            save_path = "/mnt/pics/{}.jpg".format(uri)
            with open(save_path, "w") as f:
                f.write(file_data)
            logging.info("{} saved".format(save_path))
        except Exception, e:
            # Rollback in case there is any error
            logging.error("db error, e: {}, sql: {}".format(e.message, sql))
            self.db.rollback()
