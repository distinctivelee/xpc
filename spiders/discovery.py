# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from xpc.items import PostItem, CommentItem

comment_api = "http://www.xinpianchang.com/article" \
                      "/filmplay/ts-getCommentApi?id=%s&ajax=1&page=%s"


class DiscoverySpider(scrapy.Spider):
    name = 'discovery'
    root_url = 'http://www.xinpianchang.com'
    allowed_domains = ['www.xinpianchang.com']
    # start_urls = ['http://www.xinpianchang.com/channel/index/id-0/sort-addtime/type-0']
    start_urls = ['http://www.xinpianchang.com/channel/index/id-0/sort-like/type-0?from=articleListPage']

    def parse(self, response):
        post_url = "http://www.xinpianchang.com/a%s?from=ArticleList"
        post_list = response.xpath('//ul[@class="video-list"]/li')
        for post in post_list:
            post_id = post.xpath('./@data-articleid').extract_first()
            thumbnail = post.xpath('./a/img/@_src').get()
            request = Request(post_url % post_id, callback=self.parse_post)
            request.meta['pid'] = post_id
            request.meta['thumbnail'] = thumbnail
            yield request
        next_page = response.xpath('//div[@class="page"]/a[last()]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_post(self, response):
        post = PostItem()
        post['pid'] = response.meta['pid']
        post['thumbnail'] = response.meta['thumbnail']
        post['title'] = response.xpath('//div[@class="title-wrap"]/h3/text()').get()
        post['preview'] = response.xpath('//div[@class="filmplay"]//img/@src').get()
        post['video'] = response.xpath('//video[@id="xpc_video"]/@src').get()
        post['video_format'] = ''#response.xpath('').get()
        post['category'] = response.xpath('//span[@class="cate v-center"]/text()').get()
        post['created_at'] = response.xpath('//span[contains(@class,"update-time")]/i/text()').get()
        post['play_counts'] = response.xpath('//i[contains(@class,"play-counts")]/@data-curplaycounts').get()
        post['like_counts'] = response.xpath('//span[contains(@class,"like-counts")]/@data-counts').get()
        post['description'] = response.xpath('//p[contains(@class, "desc")]/text()').get()
        yield post

        request = Request(comment_api % (post['pid'], 1), callback=self.parse_comment)
        request.meta['pid'] = post['pid']
        request.meta['cur_page'] = 1
        yield request

    def parse_comment(self, response):
        if response.text:
            total_pages = response.xpath('//li[last()]/@data-totalpages').get()
            print('-' * 50, total_pages)
            cur_page = response.meta['cur_page']
            pid = response.meta['pid']
            if total_pages and total_pages.isdigit():
                total_pages = int(total_pages)
                if total_pages > cur_page:
                    request = Request(comment_api % (pid, cur_page + 1), callback=self.parse_comment)
                    request.meta['pid'] = pid
                    request.meta['cur_page'] = cur_page + 1
                    yield request

            comments = response.xpath('//li')
            for comment in comments:
                c = CommentItem()
                user_page = '%s%s' % (self.root_url, comment.xpath('./a[1]/@href').get())
                request = Request(user_page, callback=self.parse_composer)
                yield request
                c['cid'] = user_page[2:]
                c['pid'] = pid
                c['created_at'] = comment.xpath('.//span[contains(@class,"send-time")]/text()').get()
                c['content'] = comment.xpath('.//div[contains(@class,"comment-con")]/text()').get()
                c['like_counts'] = comment.xpath('.//i[@class="counts"]/text()').get()
                yield c

    def parse_composer(self, response):
        composer = {}
        composer['name'] = response.xpath('//p[contains(@class, "creator-name")]/text()').get()
        composer['intro'] = response.xpath('//p[contains(@class, "creator-desc")]/text()').get()
        yield composer

