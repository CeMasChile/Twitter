#!/bin/bash
ROOT_DIR=/home/cemas/Twitter/codigo
BIN_PATH=$ROOT_DIR/env/bin
SPIDER=TweetScraper
cd $ROOT_DIR/TweetScraper
$BIN_PATH/scrapy crawl $SPIDER -a query="near:chile since:2019-10-11" -a lang="es"

