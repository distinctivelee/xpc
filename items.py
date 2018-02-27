# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class PostItem(scrapy.Item):
    """保存视频信息的item"""
    pid = Field()
    title = Field()
    thumbnail = Field()
    preview = Field()
    video = Field()
    video_format = Field()
    category = Field()
    created_at = Field()
    play_counts = Field()
    like_counts = Field()
    description = Field()


class CommentItem(scrapy.Item):
    commentid = Field()
    pid = Field()
    cid = Field()
    created_at = Field()
    content = Field()
    like_counts = Field()