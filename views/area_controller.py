# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,jsonify,Response
from database.models import Area,db
area_controller=Blueprint("area_controller",__name__)
@area_controller.route("/m1/public/get_area_list",methods=['POST'])
def get_area_list():
    result={'code':0,'msg':''}
    try:
        query=request.get_json()        
        area_name=query.get('area_name')
        if area_name:
            areas=Area.query.filter(Area.area_name.like(area_name+'%')).order_by('sort','area_id').all()
            
        else:
            areas=Area.query.order_by('sort','area_id').all()
        areas_arr=[]
        for area in areas :
            areas_arr.append(area.get_map())
        result['areas']=areas_arr
        result['code']=1
    except Exception,e:
        result['msg']=e.message
        
    return Response(json.dumps(result))
            
        
        
    
    
    