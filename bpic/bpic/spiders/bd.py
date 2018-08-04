# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from urllib import quote
# splash lua script
script = """
         function main(splash, args)
             assert(splash:go(args.url))
             assert(splash:wait(args.wait))
             js = string.format("document.querySelector('#kw').value=%s;document.querySelector('#su').click()", args.phone)
             splash:evaljs(js)
             assert(splash:wait(args.wait))
             return splash:html()
         end
         """
script2 = """
        function main(splash, args)
            splash:go(args.url)
            splash:wait(args.load_wait)
            splash:runjs(string.format("document.querySelector('#kw').value = '%s';", args.what_the_fuck_name))
            splash:runjs("document.querySelector('.s_btn_wr>input').click();")
            splash:wait(args.render_wait)
            splash:runjs("document.body.scrollTop=100000")
            splash:wait(args.render_wait)
            splash:runjs("document.body.scrollTop=100000")
            splash:wait(args.render_wait)
            splash:runjs("document.body.scrollTop=100000")
            splash:wait(args.render_wait)
            return splash:html()
        end
        """
class BdSpider(scrapy.Spider):
    name = 'bd'
    allowed_domains = ['image.baidu.com']
    url = 'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=index&fr=&hs=0&xthttps=111111&sf=1&fmq=&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%E6%97%A5%E6%9C%AC%E5%A5%B3%E4%BC%98'

    # start request
    def start_requests(self):
        yield SplashRequest(self.url, callback=self.parse, endpoint='execute',
                args={'lua_source': script2, 'what_the_fuck_name': u'日本性感', 'load_wait': 2, 'render_wait': 5})

    # parse the html content
    def parse(self, response):
        info = response.css('img.main_img').xpath('@data-imgurl').extract()
        print('=' * 40)
        print('\n'.join(info))
        print('=' * 40)
