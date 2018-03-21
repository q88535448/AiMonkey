# -*- coding: utf-8 -*-
__author__ = 'xiaqing'

"""
@author:xiaqing
@time: 16/11/16 下午3:25
"""
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name='AI_Monkey',
    keywords='',
    version=1.0,
    packages=find_packages(),
    url='',
    license='MIT',
    author='xaiqing',
    author_email='xiaqing@cmcm.cosudom',
    description='',
    install_requires=[
        'pyyaml', 'Appium-Python-Client', 'selenium', 'termcolor', 'uiautomator'
    ]
)