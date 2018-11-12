"""
    povpi
    Entry file for Persistence of Vision Pi
"""

from flask import Flask

app = Flask(__name__, static_folder="./static/dist",
            template_folder="./static")
app.config.from_object('povpi.config')

import povpi.views