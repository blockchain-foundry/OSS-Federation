#!/usr/bin/env python2
import sys
import math
import time
import abc
import json
import Queue
import threading
import urllib2
import logging

from bs4 import BeautifulSoup
from pyquery import PyQuery

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from chart.models import Tx, Block
from chart.config import API_SERVER_HOST, API_SERVER_PORT

logger = logging.getLogger(__name__)

class BaseCrawler(object):
    
    def __init__(self):
        # need to override self.url for crawling different ginfo's api
        self.DB = 'chart_db'
        self.url = "ginfo@apiserver"
        self.threads = []
        self.concurrency = 0
        self.max_outstanding = 16
        self.concurrency_lock = threading.Lock()
        self.since_time = 0
        self.page_queue = Queue.LifoQueue() 
    
    @abc.abstractmethod
    def init_queue(self):
        # get the newest model object in db
        raise NotImplementedError("Please Implement this method")

    # entry point for the crawler
    def start(self):
        self.init_queue()
        self.spawn_new_worker()
        
        # main thread should wait until all its childs done
        while self.threads:
            try:
                for t in self.threads:
                    t.join(1)
                    if not t.isAlive():
                        self.threads.remove(t)
            except KeyboardInterrupt, e:
                sys.exit(1)
    
    # first-phase job for each worker
    @abc.abstractmethod
    def get_soup_by(self, page_id):
        raise NotImplementedError("Please Implement this method")

    # second-phase job for each worker
    @abc.abstractmethod
    def grab_into_db(self,  soup):
        raise NotImplementedError("Please Implement this method")

    def spawn_new_worker(self):
        self.concurrency_lock.acquire()
        self.concurrency += 1
        t = threading.Thread(target=self.consumer, args=(self.concurrency,))
        t.daemon = True
        self.threads.append(t)
        t.start()
        self.concurrency_lock.release()

    def consumer(self, tid):
        while not self.page_queue.empty():
            try:
                logger.info('* Starting thread %d' % tid)
                page = self.page_queue.get()
                logger.info('[%s]: page %s' %(tid, page))
                
                soup = self.get_soup_by(page)
                if self.concurrency < self.max_outstanding:
                    self.spawn_new_worker()
                
                self.grab_into_db(soup)
                
            except Queue.Empty, e:
                logger.info('All pages have been queried')
                
        self.concurrency_lock.acquire()
        self.concurrency -= 1
        self.concurrency_lock.release()


class TxCrawler(BaseCrawler):
    
    def __init__(self):
        super(TxCrawler, self).__init__()
        #self.url = "http://140.112.29.198:8080/api/v1/tx-chart?type=longest"
        self.url = '%s:%s/api/v1/tx-chart?type=longest' % (API_SERVER_HOST, API_SERVER_PORT)

    def init_queue(self):
        # get the newest tx_time in DB
        try:
            last_tx = Tx.objects.using(self.DB).latest('tx_ntime')
            self.since_time = last_tx.tx_ntime
        except ObjectDoesNotExist:
            logger.info( 'DB have no data, try to initialize')
        
        url = '%s&since=%s&verbose=%s' % (self.url, self.since_time, 0)
        doc = PyQuery(url)
        
        total_pages = json.loads(doc('p').text())['data']['num_pages']
        for page in range(int(total_pages)):
            self.page_queue.put(page+1)

    # first-phase job
    def get_soup_by(self, page_id):
        url = '%s&since=%s&page=%s' % (self.url, self.since_time, page_id)
        try:
            page = urllib2.urlopen(url)
            soup = BeautifulSoup(page.read())
            return soup 
        except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException) as e:
            logger.error('URLError = %s' % (str(e),))
        
    # second-phase job
    def grab_into_db(self,  soup):
        rows = json.loads(soup.get_text())['data']['transaction']
        
        for row in rows:
            tx = Tx(tx_id = row['tx_index'],
                    tx_hash = row['hash'],
                    tx_type = row['type'],
                    tx_color = row['color'],
                    total_in = row['total_in'],
                    total_out = row['total_out'],
                    tx_ntime = row['time']
                    )
            tx.save(using=self.DB)


class BlockCrawler(BaseCrawler):
    
    def __init__(self):
        super(BlockCrawler, self).__init__()
        #self.url = "http://140.112.29.198:8080/api/v1/blk-chart"
        self.url = '%s:%s/api/v1/blk-chart' % (API_SERVER_HOST, API_SERVER_PORT)
    
    def init_queue(self):
        # get the newest block_ntime in DB
        try:
            last_block = Block.objects.using(self.DB).latest('block_ntime')
            self.since_time = last_block.block_ntime
        except ObjectDoesNotExist:
            logger.info('DB have no data, try to initialize')
        
        url = '%s?verbose=%s&since=%s' % (self.url, 0, self.since_time)
        doc = PyQuery(url)
        
        total_count = json.loads(doc('p').text())['data']['total_count']
        total_pages = math.ceil(total_count /500.0) 
        for idx in range(int(total_pages)):
            self.page_queue.put(idx+1)

    # first-phase job
    def get_soup_by(self, page_id):
        url = '%s?since=%s&page=%s' % (self.url, self.since_time, page_id)
        try:
            page = urllib2.urlopen(url)
            soup = BeautifulSoup(page.read())
            return soup 
        except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException) as e:
            logger.error('URLError = %s' % (str(e),))
        
    # second-phase job
    def grab_into_db(self,  soup):
        rows = json.loads(soup.get_text())['data']['block']
        
        for row in rows:
            block = Block(block_id = row['block_index'],
                          block_hash = row['hash'],
                          block_miner = row['miner'],
                          block_hashmerkleroot = row['mrklroot'],
                          block_ntime = row['time'],
                          block_height = row['height']
                        )
            block.save(using=self.DB)

def blk_worker():
    bc = BlockCrawler()
    bc.start()

def tx_worker():
    tc = TxCrawler()
    tc.start()


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        master_threads = []
        t1 = threading.Thread(target=blk_worker)
        t2 = threading.Thread(target=tx_worker)
        master_threads.append(t1)       
        master_threads.append(t2)
        t1.daemon = True
        t2.daemon = True
        
        t1.start()
        t2.start()
        while master_threads:
            try:
                for t in master_threads:
                    t.join(1)
                    if not t.isAlive():
                        master_threads.remove(t)
            except KeyboardInterrupt, e:
                sys.exit(1)


if __name__ =='__main__':
    bc = BlockCrawler()
    bc.start()
