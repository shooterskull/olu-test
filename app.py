# Author: Lee Shen Juin
# -*- coding:utf8 -*-
# !/usr/bin/env python

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import boto3
import json
import os

from flask import Flask
from flask import request
from flask import make_response

from flask.ext.sqlalchemy import SQLAlchemy

from routing import shortestpath

# Flask app should start in global layout
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['AWS_ACCESS_KEY_ID'] = os.environ['AWS_ACCESS_KEY_ID']
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ['AWS_SECRET_ACCESS_KEY']

db = SQLAlchemy(app)
from models import Shop

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "mallNavigation":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    src = parameters.get("from")
    dst = parameters.get("to")

    srcUnit, dstUnit = getUnit(src, dst)
    graph = getGraph()
    path = shortestpath(graph, srcUnit, dstUnit)

    images = getImages(path)
    imageMsgs = generateMessages(images)

    res = makeWebhookResult(imageMsgs)
    return res


def getGraph():
    s3Client = boto3.client('s3')
    response = s3Client.get_object(Bucket='jem-graphs', Key='jem_level_4.json')['Body']
    graph = json.loads(response.read())
    return graph


def getUnit(src, dst):
    srcUnit = Shop.query.filter_by(name=src).first().unit
    dstUnit = Shop.query.filter_by(name=dst).first().unit
    return srcUnit, dstUnit


def getImages(units):
    imageUrls = []
    for unit in units:
        imageUrls.append(Shop.query.get(unit).imageurl)
    return imageUrls


def generateMessages(images):
    messages = []
    for image in images:
        messages.append({"type": 3, "imageUrl": image})
    return messages


def makeWebhookResult(msgs):
    speech = "Follow this path of shops. Images of the shops are shown below. You will reach your destination at the final shop."
    message = [
                {
                    "type": 0,
                    "speech": speech
                }
    ]
    message += msgs

    return {
        "speech": "",
        "messages": message,
        # "contextOut": [],
        "source": "shop-nav-webhook"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')