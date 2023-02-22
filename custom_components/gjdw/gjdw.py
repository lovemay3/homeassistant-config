#!/usr/bin/env python
# encoding: utf-8

import requests
import logging


_Log=logging.getLogger(__name__)


AUTH_URL = 'http://weixin.bj.sgcc.com.cn/ott/app/auth/authorize?target=M_YECX'
CONSNO_URL = 'http://weixin.bj.sgcc.com.cn/ott/app/follower/consumer/prepaid/list'
REMAIN_URL = 'http://weixin.bj.sgcc.com.cn/ott/app/elec/account/query'
DETAIL_URL = 'http://weixin.bj.sgcc.com.cn/ott/app/electric/bill/overview'

class DetailInfo:
    remain: str #余额
    last_date: str #余额最后计算时间
    latest_month: str #最近的一个月（一般就是上一个月）
    latest_electricity: float #最近的一个月的电量
    latest_total: float #最近的一个月的电费
    current_year_total: float #今年的总电费
    current_year_electricity: float #今年的总电量

class GJDWData:

    @property
    def info(self):
        """Return the state of the sensor."""
        return self._info

    def __init__(self,openid):
        self._openid = openid
        self._session = 'SESSION=233f434d-a387-47bc-8cd6-45aad109506b'
        self._consNo = ''
        self._info = DetailInfo()


    def getToken(self):
        _Log.debug('[GJDWData]get token ... \n')
        headers = {
            'Host':'weixin.bj.sgcc.com.cn',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Upgrade-Insecure-Requests':'1',
            'Cookie': self._session + ';user_openid=' + self._openid,
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x1800072c) NetType/WIFI Language/zh_CN',
            'Accept-Language':'zh-cn',
            'Accept-Encoding':'gzip, deflate',
            'Connection':'keep-alive',
        }   
        r = requests.get(AUTH_URL,headers=headers,allow_redirects=False)
        response_headers = r.headers
        if 'Set-Cookie' in response_headers:
            set_cookie = response_headers['Set-Cookie']
            self._session = set_cookie.split(';')[0]     
            _Log.debug(self._session)
        else:
            _Log.debug('[GJDWData]headers:' + str(response_headers) + '\n')

    def commonHeaders(self):
        headers = {
            'Host':'weixin.bj.sgcc.com.cn',
            'Accept':'*/*',
            'X-Requested-With':'XMLHttpRequest',
            'Accept-Language':'zh-cn',
            'Accept-Encoding':'gzip, deflate',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin':'http://weixin.bj.sgcc.com.cn',
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x1800072c) NetType/WIFI Language/zh_CN',
            'Connection':'keep-alive',
            'Cookie': self._session + ';user_openid=' + self._openid,
        }
        return headers

    def getConsNo(self):  
        _Log.debug('[GJDWData] getConsNo ... \n')  
        headers = self.commonHeaders()
        r = requests.post(CONSNO_URL,headers=headers)
        result = r.json()
        if result['status'] == 0:
            self._consNo = result['data'][0]['consNo']
            _Log.debug(self._consNo)
        else:
            _Log.debug('getConsNo:获取错误:' + result['msg'])

    def getRemain(self):
        _Log.debug('[GJDWData]getRemain ... \n')
        headers = self.commonHeaders()
        data = {
            'consNo':self._consNo
        }
        r = requests.post(REMAIN_URL,data,headers=headers)
        result = r.json()
        if result['status'] == 0:
            
            self._info.remain = result['data']['BALANCE_SHEET']
            self._info.last_date = result['data']['AS_TIME']

            _Log.debug(self._info.remain)
        else:
            _Log.debug('getRemain:获取错误:' + result['msg'])

    def getDetail(self):
        _Log.debug('[GJDWData]getDetail ... \n')
        headers = self.commonHeaders()
        params = {
            'consNo':self._consNo
        }
        r = requests.get(DETAIL_URL,params=params,headers=headers)        
        result = r.json()
        if result['status'] == 0:
            data = result['data']
            self._info.latest_month = data['lastMonth']
            self._info.latest_electricity = data['SUM_ELEC']
            self._info.latest_total = data['SUM_ELECBILL']
            self._info.current_year_electricity = data['TOTAL_ELEC']
            self._info.current_year_total = data['TOTAL_ELECBILL']
            _Log.debug(self._info.current_year_total)
        else:
            _Log.debug('getDetail:获取错误:' + result['msg'])                
        pass

    def getData(self):
        self.getToken()
        self.getConsNo()
        self.getRemain()
        self.getDetail()
# data = GJDWData('xx')
# data.getToken()
# data.getConsNo()
# data.getRemain()
# data.getDetail()

# r = requests.post(url,data,headers=headers)

# print(r.text)


