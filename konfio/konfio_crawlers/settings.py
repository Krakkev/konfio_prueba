# -*- coding: utf-8 -*-

# Scrapy settings for konfio_crawlers project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import os
path = os.getcwd()

BOT_NAME = 'konfio_crawlers'

SPIDER_MODULES = ['konfio_crawlers.spiders']
NEWSPIDER_MODULE = 'konfio_crawlers.spiders'


DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

SPLASH_URL = 'http://localhost:8050/'
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    'scrapy_deltafetch.DeltaFetch': 100,
}
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'jobs_australia (+http://www.yourdomain.com)'

# Enable deltafetch middleware

DELTAFETCH_ENABLED = True
DELTAFETCH_DIR = path+"/deltafetch/"

# DOWNLOAD DELAY BTN 1-3 SEC
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 4

#cookies enabled
# SPLASH_COOKIES_DEBUG= True

# CLOSESPIDER_TIMEOUT = 36000

# CLOSESPIDER_ITEMCOUNT = 7000

CONCURRENT_REQUESTS = 1

#DOWNLOAD_DELAY = 2
