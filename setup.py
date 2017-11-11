#/usr/bin/env python3
#-*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
	name='ahttp',
	version='1.0.0',
	description='Based on aiohttp and asyncio requests',
    long_description='The Instructions of ahttp at https://github.com/web-trump/ahttp.git',
	install_requires=['aiohttp>=1.3.5',] ,
	author='LiShenGang',
	author_email='cszy2013@163.com',
	license='BSD License',
	py_modules= ['ahttp'] ,
	platforms=["python 3.5+"],
	url='https://github.com/web-trump/ahttp.git',
	classifiers=[
		'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3.5',
		],
)