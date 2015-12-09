#!/usr/bin/env python
# encoding: utf-8
__author__ = 'rui'

import time
import urllib
import hashlib
import json
import requests


###
# 百度云推送服务端SDK Python版本
# @version 1.0.0
###


class Channel(object):
    """
    Channel类提供百度云推送服务端SDK的Python版本，
    用户首先实例化这个类，设置自己的apiKey和secretKey，即可使用Push服务接口
    """
    # 用户发起请求时的unix时间戳。本次请求签名的有效时间为该时间戳+10分钟
    TIMESTAMP = 'timestamp'

    # 用户指定本次请求签名的失效时间。格式为unix时间戳形式
    EXPIRES = 'expires'

    # API版本号，默认使用最高版本
    VERSION = 'v'

    # 通道标识
    CHANNEL_ID = 'channel_id'

    # 用户标识
    USER_ID = 'user_id'

    # 设备类型。如果存在此字段，则只返回该设备类型的绑定关系；默认不区分设备类型
    DEVICE_TYPE = 'device_type'

    # 可选设备类型
    DEVICE_BROWSER = 1
    DEVICE_PC = 2
    DEVICE_ANDRIOD = 3
    DEVICE_IOS = 4
    DEVICE_WINDOWSPHONE = 5

    # 查询起始页码，默认为0
    START = 'start'

    # 一次查询条数，默认为10
    LIMIT = 'limit'

    # 指定消息内容，单个消息为单独字符串
    MESSAGES = 'messages'

    # 删除的消息id列表，由一个或多个msg_id组成，多个用json数组表示
    MSG_IDS = 'msg_ids'

    # 消息标识。指定消息标识，自动覆盖相同消息标识的消息，只支持android、browser、pc三种设备类型。
    MSG_KEYS = 'msg_keys'

    # 消息类型，0：消息（透传），1：通知，默认为0
    MESSAGE_TYPE = 'message_type'

    # 可选消息类型
    PUSH_MESSAGE = 0
    PUSH_NOTIFICATION = 1

    # 指定消息的过期时间，默认为86400秒。
    MESSAGE_EXPIRES = 'message_expires'

    # 标签名，可按标签分组
    TAG_NAME = 'tag'

    # 标签信息
    TAG_INFO = 'info'

    # 标签ID
    TAG_ID = 'tid'

    # 访问令牌，明文AK，可从此值获得App的信息，配合sign中的sk做合法性身份认证。
    API_KEY = 'apikey'

    # 开发者密钥，用于调用HTTP API时进行签名加密，以证明开发者的合法身份。
    SECRET_KEY = 'secret_key'

    # Channel常量
    SIGN = 'sign'
    METHOD = 'method'
    HOST = 'host'
    PRODUCT = 'channel'
    DEFAULT_HOST = 'channel.api.duapp.com'

    # 证书相关常量
    NAME = 'name'
    DESCRIPTION = 'description'
    CERT = 'cert'
    RELEASE_CERT = 'release_cert'
    DEV_CERT = 'dev_cert'

    # 推送类型
    PUSH_TYPE = 'push_type'

    # 可选推送类型
    PUSH_TO_USER = 1
    PUSH_TO_TAG = 2
    PUSH_TO_ALL = 3

    # Channel错误常量
    CHANNEL_SDK_SYS = 1
    CHANNEL_SDK_INIT_FAIL = 2
    CHANNEL_SDK_PARAM = 3
    CHANNEL_SDK_HTTP_STATUS_ERROR_AND_RESULT_ERROR = 4
    CHANNEL_SDK_HTTP_STATUS_OK_BUT_RESULT_ERROR = 5

    ###
    # 对外接口
    ###

    def __init__(self, apiKey, secretKey):
        self._apiKey = apiKey
        self._secretKey = secretKey
        self._requestId = 0
        self._method_channel_in_body = ['push_msg', 'set_tag', 'fetch_tag', 'delete_tag', 'query_user_tags']

    def setApiKey(self, apiKey):
        self._apiKey = apiKey

    def setSecretKey(self, secretKey):
        self._secretKey = secretKey

    def getRequestId(self):
        return self._requestId

    # 查询设备、应用、用户与百度Channel的绑定关系
    def queryBindList(self, userId, optional=None):
        """
        参数：
            str userId：用户ID号
            dict optional：可选参数
        返回值：
            成功：python字典；失败：False
        """
        tmpArgs = [userId, optional]
        arrArgs = self._mergeArgs([Channel.USER_ID], tmpArgs)
        arrArgs[Channel.METHOD] = 'query_bindlist'
        return self._commonProcess(arrArgs)

    # 推送消息，该接口可用于推送单个人、一群人、所有人以及固定设备的使用场景
    def pushMessage(self, push_type, messages, message_keys, optional=None):
        """
        参数：
            push_type：推送消息的类型
            messages：消息内容
            message_keys：消息key
            optional：可选参数
        返回值：
            成功：python字典；失败：False
        """
        tmpArgs = [push_type, messages, message_keys, optional]
        arrArgs = self._mergeArgs([Channel.PUSH_TYPE, Channel.MESSAGES, Channel.MSG_KEYS], tmpArgs)
        arrArgs[Channel.METHOD] = 'push_msg'
        arrArgs[Channel.PUSH_TYPE] = push_type
        arrArgs[Channel.MESSAGES] = json.dumps(arrArgs[Channel.MESSAGES])
        arrArgs[Channel.MSG_KEYS] = json.dumps(arrArgs[Channel.MSG_KEYS])
        return self._commonProcess(arrArgs)

    # 判断设备、应用、用户与Channel的绑定关系是否存在
    def verifyBind(self, userId, optional=None):
        """
        参数：
            userId：用户id
            optional：可选参数
        返回值：
            成功：python数组；失败：False
        """
        tmpArgs = [userId, optional]
        arrArgs = self._mergeArgs([Channel.USER_ID], tmpArgs)
        arrArgs[Channel.METHOD] = 'verify_bind'
        return self._commonProcess(arrArgs)

    # 查询离线消息
    def fetchMessage(self, userId, optional=None):
        """
        参数：
            userId：用户id
            optional：可选参数
        返回值：
            成功：python字典；失败：False
        """
        tmpArgs = [userId, optional]
        arrArgs = self._mergeArgs([Channel.USER_ID], tmpArgs)
        arrArgs[Channel.METHOD] = 'fetch_msg'
        return self._commonProcess(arrArgs)

    # 查询离线消息的个数
    def fetchMessageCount(self, userId, optional=None):
        """
        参数：
            userId：用户id
            optional：可选参数
        返回值：
            成功：python字典；失败：False
        """
        tmpArgs = [userId, optional]
        arrArgs = self._mergeArgs([Channel.USER_ID], tmpArgs)
        arrArgs[Channel.METHOD] = 'fetch_msgcount'
        return self._commonProcess(arrArgs)

    # 删除离线消息
    def deleteMessage(self, userId, msgId, optional=None):
        """
        参数：
            userId：用户id
            msgIds：消息id
            optional：可选参数
        返回值：
            成功：python字典；失败：False
        """
        tmpArgs = [userId, msgId, optional]
        arrArgs = self._mergeArgs([Channel.USER_ID, Channel.MSG_IDS], tmpArgs)
        arrArgs[Channel.METHOD] = 'delete_msg'
        if isinstance(arrArgs[Channel.MSG_IDS], list):
            arrArgs[Channel.MSG_IDS] = json.dumps(arrArgs[Channel.MSG_IDS])
        return self._commonProcess(arrArgs)

    # 服务器端设置用户标签。
    # 当该标签不存在时，服务端将会创建该标签。特别地，当user_id被提交时，服务端将会完成用户和tag的绑定操作。
    def setTag(self, tagName, optional=None):
        """
        参数：
            tagName：标签
            optional：可选参数
        返回值：
            成功：python字典；失败：False
        """
        tmpArgs = [tagName, optional]
        arrArgs = self._mergeArgs([Channel.TAG_NAME], tmpArgs)
        arrArgs[Channel.METHOD] = 'set_tag'
        return self._commonProcess(arrArgs)

    # App Server查询应用标签
    def fetchTag(self, optional=None):
        """
        参数：
            optional：可选参数
        返回值：
            成功：python字典；失败：False
        """
        tmpArgs = [optional]
        arrArgs = self._mergeArgs([], tmpArgs)
        arrArgs[Channel.METHOD] = 'fetch_tag'
        return self._commonProcess(arrArgs)

    # 服务端删除用户标签。
    # 特别地，当user_id被提交时，服务端将只会完成解除该用户与tag绑定关系的操作。
    # 注意：该操作不可恢复，请谨慎使用。
    def deleteTag(self, tagName, optional=None):
        """
        参数：
            tagName：标签
            optional：可选参数
        返回值：
            成功：python字典；失败：False
        """
        tmpArgs = [tagName, optional]
        arrArgs = self._mergeArgs([Channel.TAG_NAME], tmpArgs)
        arrArgs[Channel.METHOD] = 'delete_tag'
        return self._commonProcess(arrArgs)

    # App Server查询用户所属的标签列表
    def queryUserTag(self, userId, optional=None):
        """
        参数：
            userId：用户id
            optional：可选参数
        返回值：
            成功：python字典；失败：False
        """
        tmpArgs = [userId, optional]
        arrArgs = self._mergeArgs([Channel.USER_ID], tmpArgs)
        arrArgs[Channel.METHOD] = 'query_user_tags'
        return self._commonProcess(arrArgs)

    # 根据channel_id查询设备类型
    def queryDeviceType(self, channelId, optional=None):
        """
        根据channelId查询设备类型
        参数：
            ChannelId：用户Channel的ID号
            optional：可选参数
        返回值：
            成功：python字典；失败：False
        """
        tmpArgs = [channelId, optional]
        arrArgs = self._mergeArgs([Channel.CHANNEL_ID], tmpArgs)
        arrArgs[Channel.METHOD] = 'query_device_type'
        return self._commonProcess(arrArgs)


    ###
    # 内部函数
    ###

    def _checkString(self, string, minLen, maxLen):
        return minLen <= len(string) <= maxLen

    def _adjustOpt(self, opt):
        if Channel.TIMESTAMP not in opt:
            opt[Channel.TIMESTAMP] = int(time.time())
        opt[Channel.HOST] = Channel.DEFAULT_HOST
        opt[Channel.API_KEY] = self._apiKey
        if Channel.SECRET_KEY in opt:
            del opt[Channel.SECRET_KEY]

    def _genSign(self, method, url, arrContent):
        gather = method + url
        keys = arrContent.keys()
        keys.sort()
        for key in keys:
            gather += key + '=' + str(arrContent[key])
        gather += self._secretKey
        sign = hashlib.md5(urllib.quote_plus(gather))
        return sign.hexdigest()

    def _baseControl(self, opt):
        resource = 'channel'
        if Channel.CHANNEL_ID in opt:
            if opt[Channel.CHANNEL_ID] and opt[Channel.METHOD] not in self._method_channel_in_body:
                resource = opt[Channel.CHANNEL_ID]
                del opt[Channel.CHANNEL_ID]

        host = opt[Channel.HOST]
        del opt[Channel.HOST]

        url = 'http://' + host + '/rest/2.0/' + Channel.PRODUCT + '/'
        url += resource
        http_method = 'POST'
        opt[Channel.SIGN] = self._genSign(http_method, url, opt)

        headers = dict()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['User-Agent'] = 'Baidu Channel Service Pythonsdk Client'

        return requests.post(url, data=opt, headers=headers)

    def _commonProcess(self, paramOpt):
        self._adjustOpt(paramOpt)
        ret = self._baseControl(paramOpt)
        result = ret.json()
        self._requestId = result['request_id']

        if ret.status_code == requests.codes.ok:
            return result
        raise Exception(result)

    def _mergeArgs(self, arrNeed, tmpArgs):
        arrArgs = dict()

        if not arrNeed and not tmpArgs:
            return arrArgs

        if len(tmpArgs)-1 != len(arrNeed) and len(tmpArgs) != len(arrNeed):
            keys = '('
            for key in arrNeed:
                keys += key + ','
            if key[-1] == '' and key[-2] == ',':
                keys = keys[0:-2]
            keys += ')'
            raise Exception('invalid sdk, params, params' + keys + 'are need', Channel.CHANNEL_SDK_PARAM)

        if len(tmpArgs)-1 == len(arrNeed) and tmpArgs[-1] is not None and (not isinstance(tmpArgs[-1], dict)):
            raise Exception('invalid sdk params, optional param must bean dict', Channel.CHANNEL_SDK_PARAM)

        idx = 0
        if isinstance(arrNeed, list):
            for key in arrNeed:
                if tmpArgs[idx] is None:
                    raise Exception('lack param ' + key, Channel.CHANNEL_SDK_PARAM)
                arrArgs[key] = tmpArgs[idx]
                idx = idx + 1

        if len(tmpArgs) == idx + 1 and tmpArgs[idx] is not None:
            for (key, value) in tmpArgs[idx].items():
                if key not in arrArgs and value is not None:
                    arrArgs[key] = value

        return arrArgs