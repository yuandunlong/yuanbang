# -*- coding: utf-8 -*-
from flask import Blueprint,current_app
from flask import request
from flask import json,jsonify,Response
from database.models import Area,db
area_controller=Blueprint("area_controller",__name__)
@area_controller.route("/m1/public/get_area_list",methods=['POST','GET'])
def get_area_list():
    result={'code':0,'msg':''}
    try:
        query=request.get_json()        
        area_name=query.get('area_name')
        if area_name:
            areas=Area.query.filter(Area.area_name.like(area_name+'%')).order_by('sort',Area.area_id).all()
            
        else:
            areas=Area.query.filter().order_by('sort',Area.area_id).all()
        areas_arr=[]
        for area in areas :
            areas_arr.append(area.get_map())
        result['areas']=areas_arr
        result['code']=1
    except Exception,e:
        current_app.logger.exception(e)
        areas=Area.query.filter().order_by('sort',Area.area_id).all()
        areas_arr=[]
        for area in areas :
            areas_arr.append(area.get_map())
        result['areas']=areas_arr
        result['code']=1        
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type="application/json")
            
        
@area_controller.route('/m1/public/get_area_list_group_by_alfa')        
def get_area_list_group_by_alfa():
    result={'code':1,'msg':''}
    try:
        result_set=Area.query.filter().order_by('sort',Area.area_id).all()
        result['areas']={}
        areas_arr=[]
        for area in result_set:
            areas_arr.append(area.get_map())
            
        for area_map in areas_arr:
            if result['areas'].has_key(area_map['sort']):
                result['areas'][area_map['sort']].append(area_map)
            else:
                result['areas'][area_map['sort']]=[]
                result['areas'][area_map['sort']].append(area_map)
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
    
    