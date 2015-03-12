# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,Response
from database.models import MobileBanner
mobile_banner_controller=Blueprint('mobile_banner_controller',__name__)

@mobile_banner_controller.route('/m1/public/get_mobile_banners',methods=['GET'])
def get_mobile_controller():
    result={'code':1,'msg':'ok'}
    try:
        items=MobileBanner.query.filter().all()
        mobile_banners=[]
        for item in items:
            mobile_banners.append(item.get_map())
        result['mobile_banners']=mobile_banners
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    
    return Response(json.dumps(result))
        
        