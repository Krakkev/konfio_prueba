import subprocess
from flask import Flask
from flask import request
from flask import render_template
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup import Items

app = Flask(__name__)


@app.route('/sources/')
def my_form():
    return render_template("crawlers_board.html")


@app.route('/products/', methods=['POST'])
def my_form_post():
    spider_name = request.form['site']
    num_items = request.form['ads']
    if spider_name:
        spider_name = spider_name.lower()
        path = "ads.json"
        if os.path.exists(path):
            os.remove(path)
        if num_items:
            try:
                items = int(num_items)
                items = items - 1  # -1 because of extra request created by scrapy
                if items >= 1:
                    items = str(items)
                else:
                    items = "9"  # default number of ads
            except:
                items = "9"  # default number of ads
        else:
            items = "9"  # default number of ads

        engine = create_engine('sqlite:///entregable/konfio.db', echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        subprocess.check_output(['scrapy', 'crawl', spider_name, "-o", path, "--set", "CLOSESPIDER_ITEMCOUNT=" + items])
        json_items = pd.read_json(path)
        for index, row in json_items.iterrows():
            new_contact = Items(row.id_item,
                                row.price,
                                row.title,
                                row.description,
                                row.site,
                                row.url)
            session.add(new_contact)
        session.commit()
        with open(path) as items_file:
            return items_file.read()


if __name__ == '__main__':
    app.run()
