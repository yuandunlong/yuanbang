# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,Response
from database.models import BuyerAddress,db
from utils import check_token
address_controller=Blueprint('address_controller',__name__)

@check_token
def get_all_addresses_by_user(token_type,info):
    
    result={'code':'1','msg':'ok'}
    
    try:
        #BuyerAddress.query.
        pass
        
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result))
        