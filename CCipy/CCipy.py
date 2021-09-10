#!/usr/bin/env python3
#-*-coding:utf-8-*-

try:
	from core.console.console import Console
except ImportError as err:
	print(err)

Console().run()
