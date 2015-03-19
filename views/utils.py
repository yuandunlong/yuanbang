# -*- coding: utf-8 -*-
from flask import request,Response,json
from database.models import db,Token,Buyer,ShopInfo
def check_token(func):
    def wrapper():
        response={'code':0,'msg':''}
        access_token=request.args.get('token','')
        
        if access_token=='':
            response['msg']='access denied,please provide token'
            return Response(json.dumps(response))
        else:
            token=Token.query.filter_by(access_token=access_token).first()
            if token:
                if token.token_type==1:
                    buyer=Buyer.query.get(token.user_id)
                    if not buyer:
                        response['msg']='wrong token'
                        return Response(json.dumps(response))
                    else:
                        info=buyer
                elif token.token_type==2:
                    shop_info=ShopInfo.query.get(token.user_id)
                    if shop_info==None:
                        response['msg']='wrong token'
                        return Response(json.dumps(response))
                    else:
                        info=shop_info
            else:
                response['msg']='token not exist'
                return Response(json.dumps(response))
        result = func(token.token_type,info)
        return result
    
    wrapper.__name__=func.__name__
    return wrapper

def result_set_converter(result_set):
    arr=[]
    if result_set:
        for result in result_set:
            arr.append(result.get_map())
    return arr

def uniqid(prefix='', more_entropy=False):
    m = time.time()
    uniqid = '%8x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
    if more_entropy:
        valid_chars = list(set(string.hexdigits.lower()))
        entropy_string = ''
        for i in range(0,10,1):
            entropy_string += random.choice(valid_chars)
        uniqid = uniqid + entropy_string
    uniqid = prefix + uniqid
    return uniqid