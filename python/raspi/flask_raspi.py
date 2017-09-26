from flask import Flask

app = Flask("raspi", 
            static_folder='../page/',
            static_url_path='')

import raspi_media
import raspi_system

@app.route("/s")
def root():
    return "sdfs"
