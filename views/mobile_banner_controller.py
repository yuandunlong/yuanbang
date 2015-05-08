# -*- coding: utf-8 -*-
from flask import Blueprint,render_template
from flask import request
from flask import json,Response,redirect
from database.models import MobileBanner,db
from werkzeug import secure_filename
from datetime import datetime
import os
import time

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
    
    return Response(json.dumps(result),content_type="application/json")
        

@mobile_banner_controller.route('/m1/public/display_mobile_banner_manage',methods=['GET'])
def display_mobile_banner_manage():
    items=MobileBanner.query.filter().all()
    mobile_banners=[]
    for item in items:
        mobile_banners.append(item.get_map())
    return render_template('mobile_banner.html',mobile_banners=mobile_banners)
    

@mobile_banner_controller.route('/m1/public/display_add_or_update_mobile_bannner/<banner_id>')
def display_add_or_update_mobile_bannner(banner_id):
    m=None
    if str.isdigit(banner_id.encode()):
        banner_id=int(banner_id)
        if int(banner_id)>0:
            m=MobileBanner.query.get(banner_id)        
    
        
    
    return render_template('add_or_update_banner.html',banner=m)
    
    
@mobile_banner_controller.route('/m1/public/save_mobile_banner',methods=['POST'])    
def save_mobile_banner():
    if request.form.get('banner_id'):
        m=MobileBanner.query.get(request.form.get('banner_id'))
    else:
        m=MobileBanner()
    m.name=request.form.get('name')
   # m.picture_url=request.form.get('picture_url')
    m.target=request.form.get('target')
    m.banner_type=request.form.get('banner_type')
    m.display_order=request.form.get('display_order')
    m.description=request.form.get('description')
    if request.files.has_key('image'):
        f=request.files['image']
        file_name='_'+str(int(time.mktime(time.localtime())))+secure_filename(f.filename)
        if f.filename!='':
            m.picture_url='uploads/'+file_name
            f.save(os.path.join(r'D:\\wamp\www\\uploads\\',file_name))
    if not m.id:
        db.session.add(m)
    db.session.commit()
    return redirect('/m1/public/display_mobile_banner_manage')
@mobile_banner_controller.route('/m1/public/delete_mobile_banner',methods=['GET'])
def delete_mobile_banner():
    
    id=request.args['id']
    sql='delete from mobile_banner where id=%s'
    db.engine.execute(sql,(id))
    return redirect('/m1/public/display_mobile_banner_manage')