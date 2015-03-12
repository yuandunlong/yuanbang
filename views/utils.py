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
        result = func(token.token_type,info)
        return result
    return wrapper