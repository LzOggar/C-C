#!/usr/bin/env python3
#-*-coding:utf-8-*-

try:
    from core.bot import Bot
except ImportError as err:
    print(err)

Bot().run()
