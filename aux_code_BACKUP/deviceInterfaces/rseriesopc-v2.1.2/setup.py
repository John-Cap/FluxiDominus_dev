# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 15:12:39 2021

@author: lechuzin
"""
from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

setup(
    name="rseriesopc",
    version="2.1.2",
    author="Edwin Barragan",
    author_email="ebarragan@emtech.com.ar",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    # package_data={'files':['src/files/example4','files/example5'],
    #               'examples':['src/examples'],
    #               'docs':['src/docs']},
    # scripts=['bin/script1','bin/script2'],
    url="http://www.emtech.com.ar",
    license="LICENSE.txt",
    description="A package for receiving RSeries Data through OPC UA",
    long_description=open("README.txt").read(),
    # python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.* , !=3.8.*',
    python_requires=">=3.7",
    install_requires=["opcua"],
    # classifiers=[
    #     'Development Status :: 3 - Alpha',
    #     'Operating System :: Microsoft :: Windows',
    #     'Programming Language :: Python',
    #     'Programming Language :: Python :: 2.7',
    #     'Programming Language :: Python :: 3',
    #     'Programming Language :: Python :: 3.5',
    #     'Programming Language :: Python :: 3.6',
    #     'Programming Language :: Python :: 3.7',
    #     'Programming Language :: Python :: 3.8',
    #     'Programming Language :: Python :: 3.9',
    #     ],
    # setup_requires=[
    #     'opcua'
    #     'unittest'],
)
