#!/bin/bash

apt-get update

apt-get install -y python python-dev

apt-get install -y python-pip

pip install pandas

pip install Flask

pip install scrapy

pip install SQLAlchemy

apt-get install python-bsddb3

apt-get install libdb5.3

pip install scrapy-deltafetch

pip install requests

pip install IPython==5.0

cd konfio

python setup.py

chmod -R 777 entregable/konfio.db
