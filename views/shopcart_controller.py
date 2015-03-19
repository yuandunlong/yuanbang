# -*- coding: utf-8 -*-
from flask import json,Response,Blueprint
from utils import check_token
from database.models import db
shopcart_controller=Blueprint('shopcart_controller',__name__)

@shopcart_controller.route('/m1/private/get_cart_list',methods=['GET','POST'])
@check_token
def get_cart_list(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
            sql='''
            SELECT
            a.GoodsID,
            a.CreateTime,
            c.PhotoPath,
            b.GoodsName,
            b.SalePrice,
            b.Discount,
            a.Quantity,
            b.SetNum,
            b.SetPrice,
            IF (
                a.Quantity >= b.SetNum,
                b.SetPrice,
                round(b.SalePrice * b.Discount, 2)
                ) AS DisPrice,
                IF (
                    a.Quantity >= b.SetNum,
                    round(b.SetPrice * a.Quantity, 2),
                    round(
                        round(b.SalePrice * b.Discount, 2) * a.Quantity,
                        2
                    )
                    ) AS Money,
                IFNULL(d.Quantity,0) AS SumQuantity
            FROM  tb_shoppingcart a
            LEFT JOIN tb_goodsinfo_s b ON a.GoodsID = b.GoodsID
            LEFT JOIN tb_photo c ON b.GoodsID = c.LinkID
            AND c.IsChecked = '1'
            AND c.IsVisable = '1'
            LEFT JOIN (
                SELECT
                GoodsID,
                SUM(Quantity) AS Quantity
                FROM
                tb_purchase_s
                GROUP BY
                GoodsID
                ) d ON a.GoodsID = d.GoodsID
            WHERE
                a.BuyerID = ?
            ORDER BY
                b.ShopID,a.GoodsID ";
            '''
            result_set=db.engine.execute(sql,[user_info.buyer_id])        
    except Exception ,e:
        result['msg']=e.message
    return Response(json.dumps(result))
    
    