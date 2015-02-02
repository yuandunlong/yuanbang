# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,jsonify
from database.models import Buyer,BuyerAddress,db
buyer_controller=Blueprint("buyer_controller",__name__)
@buyer_controller.route('/test')
def test():
    buyer=Buyer.query.filter().first()
    ba=BuyerAddress.query.filter_by(buyer_id=9)[0]
    return u"用户="+buyer.get_json()
