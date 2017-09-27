from flask import Flask, redirect 

app = Flask("raspi", 
            static_folder='../page/',
            static_url_path='')

import raspi_media
import raspi_system
import raspi_youtube

@app.route("/")
def root():
    return redirect("/raspi/index.html")
