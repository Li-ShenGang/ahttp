#/usr/bin/env python3
#-*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
	name='ahttp',
	version='0.0.1',
	description='The Fastest Speed Asynchronous HTTP Requests',
    long_description=open('README.md').read(),
	install_requires=['aiohttp>=1.3.5',] ,
	author='LiShenGang',
	author_email='cszy2013@163.com',
	license='BSD License',
	packages=find_packages(),
	platforms=["all"],
	url='https://www.github.com',
	classifiers=[
		'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3.5',
		],
)