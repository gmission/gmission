<?php
/**
 * *************************************************************************
 *
 * Copyright (c) 2012 Baidu.com, Inc. All Rights Reserved
 *
 * ************************************************************************
 */

/**
 * Baidu push service sdk for php
 * @file sdk.php
 *
 * 
 *        
 */


if(!defined('PUSH_SDK_HOME')){
    define('PUSH_SDK_HOME', dirname(__FILE__));
}

//echo PUSH_SDK_HOME;

require_once PUSH_SDK_HOME . '/configure.php';
require_once PUSH_SDK_HOME . '/lib/BaseSDK.php';
require_once PUSH_SDK_HOME . '/lib/AssertHelper.php';

/**
 *
 * <i>
 * Notice: 在推送当msg_type为1的时候, 尽量使msg以array方式进行传递, 便于进行参数检查.
 * 其中一个必要的检查内容是, msg体必须包含description, 在使用string进行传递时, 方法内部将无法进行这些检查,只能等待服务器检查后返回错误
 * </i>
 *
 * @method boolean pushMsgToSingleDevice(string $channel_id, string|array $msg, array $opts)
 *         单播, 推送一条消息到指定设备<br />
 *         <b>
 *         $channel_id 目标客户端设备所属的唯一id;<br />
 *         $msg 消息内容.可参见<u>消息体格式说明</u> 当消息体类型为一个array时,将自动调用json_encode方法来将array转换为一个string;<br />
 *         $opts 可选参数列表, 包含 msg_type, msg_expires, deploy_status, topic_id几项可选内容; <br />
 *        
 * @method boolean pushMsgToAll(string|array $msg, array $opts)
 *         广播, 推送一条消息到全部设备
 *         <b>
 *         $msg 当消息体类型为一个array时,将自动调用json_encode方法来将array转换为一个string;<br />
 *         $opts 可选参数, 包含 msg_type, msg_expires, deploy_status几项可选内容; <br />
 *        
 * @method boolean pushMsgToTag(string $tag, string|array $msg,array $opts)
 *         组播, 推送一条消息到一组设备.
 *         <b>
 *         $tag 组名,
 *         $msg 消息内容.可参见<u>消息体格式说明</u> 当消息体类型为一个array时,将自动调用json_encode方法来将array转换为一个string;<br />
 *         $opts 可选参数, 包含 msg_type, msg_expires, deploy_status几项可选内容; <br />
 *         
 * @method boolean pushToSmartTag(string $type, string|array $msg, array $opts)
 *         组播, 根据$type类型，向指定标签组推送消息
 *         <b>
 *         $type 标签组类型<br />
 *         $msg 消息内容.可参见<u>消息体格式说明</u> 当消息体类型为一个array时,将自动调用json_encode方法来将array转换为一个string;<br />
 *         $opts 可选参数, 包含 selector, msg_type, msg_expires, deploy_status, send_time几项可选内容; <br />
 *         
 * @method boolean pushBatchUniMsg(string $channel_ids, string $msg);
 *         批量单播, 向指定的一组channel_id发送一条消息. 
 *         <br/>
 *         $channel_ids; 一个数组, 每项为一个channel_id <br />
 *         $msg 消息内容.可参见<u>消息体格式说明</u> 当消息体类型为一个array时,将自动调用json_encode方法来将array转换为一个string;<br />
 *         $opts 可选参数, 包含
 * 
 * @method boolean queryMsgStatus(string $msg_id); 
 *         查询消息发送状态
 *         <br/>
 *         $msg_id 在发送时, 由服务端返回的 msg_id
 *
 * @method boolean queryTimerRecords(string $timer_id, array $opts); 
 *         根扰timer_id查询一个定时或周期的消息发送记录
 *         <br/>
 *         $timer_id 在发送消息时,由服务端产生的timer_id
 *         $opts 可选参数, 包含 start, limit, start_time, end_time等几项可选内容;<br />
 *
 * @method boolean queryTopicRecords(string $topic_id, array $opts);
 *         根扰topic查询一个topic下的消息发送记录 
 *         <br/>
 *         $topic_id 发送消息时指定的topic
 *         $opts 可选参数, 包含
 *         
 * @method boolean queryTimerList(array $opts); 
 *         查询当前应用下的定时消息及周期消息.
 *         <br/>
 *         $opts 可选参数, 包含timer_id, start, limit等几项可选内容, 当指定timer_id时, 仅返回目标timer相关的信息.
 *         
 * @method boolean createTag(string $tag); 
 *         创建一个tag
 *         <br/>
 *         $tag tag名称
 *         
 * @method boolean deleteTag(string $tag);
 *         删除一个tag 
 *         <br/>
 *         $tag tag名称
 *         
 * @method boolean queryTags(array $opts);
 *         查询当前应用下的tag列表 
 *         <br>
 *         $opts 可选参数, 包含tag, start, limit, 当指定tag时, 仅返回目标tag相关信息
 *         
 * @method boolean addDevicesToTag(string $tag, string $channel_ids);
 *         向一个tag下添加设备 
 *         <br/>
 *         $tag tag名称 <br />
 *         $channel_ids 需要添加的一组channel_id
 *         
 * @method boolean delDevicesFromTag(string $tag, string $channel_ids); 
 *         从一个tag下删除一批设备 
 *         <br/>
 *         $tag; <br />
 *         $channel_ids 需要删除的一组channel_id
 *         
 * @method boolean queryDeviceNumInTag(string $tag); 
 *         查询一个tag下的设备数量
 *         <br/>
 *         $tag tag名称
 *         
 */
class PushSDK extends BaseSDK {
    const VERSION = '3.0.0';
    
    const TAG_TYPE_LBS_LABEL = 2;       // LBS 推送
    const TAG_TYPE_INTEREST_LABEL = 3;  // 兴趣组
    const TAG_TYPE_AGE_LABEL = 4;       // 年龄组
    const TAG_TYPE_SEX_LABEL = 5;       // 性别组
    const TAG_TYPE_OP_LABEL = 6;        // 组合运算
    
    // required必须存在, 如果不存在必要参数. 请留空数组, optional为可选.不需要可以不写.
    
    /**
     * 为兼容php 5.2及5.4,不支持将const写成array.
     * 
     * 获得一个方法映射关系的array.
     * @return multitype:multitype:string multitype:string   multitype:string multitype: multitype:string   multitype:string multitype: multitype:string multitype:string
     */
    private function getMapping(){
        /**
         * restApi 方法映射. 
         * 
         * 每项描述一个method的 包含以下内容:
         *      url: string 方法调用位置
         *      required: array<K,V> 必须的参数列表,K有参数名, V为验证条件
         *      optional: array<K,V> 可选的参数列表,K有参数名, V为验证条件
         *      before: string 指定一个预处理方法. 用于在发送http request之前对payload内容进行一次处理.
         * 
         * @var array
         */
        $apiMapping = array (
            'pushMsgToSingleDevice' => array (
                'url' => '/push/single_device',
                'required' => array (
                    'channel_id' => self::$fieldIdStr,
                    'msg' => self::$fieldMsg,
                ),
                'optional' => array (
                    'msg_type' => self::$fieldMsgType,
                    'msg_expires' => self::$fieldMsgExpires,
                    'deploy_status' => self::$fieldDeployStatus,
                    //'topic_id' => self::$fieldMsgTopic,
                ),
                'before' => 'verifyMessage',
            ),
            'pushMsgToAll' => array (
                'url' => '/push/all',
                'required' => array (
                    'msg' => self::$fieldMsg,
                ),
                'optional' => array (
                    'msg_type' => self::$fieldMsgType,
                    'msg_expires' => self::$fieldMsgExpires,
                    'deploy_status' => self::$fieldDeployStatus,
                    'send_time' => self::$fieldSendTime,
                ),
                'before' => 'verifyMessage',
            ),
            'pushMsgToTag' => array (
                'url' => '/push/tags',
                'required' => array (
                    'tag' => self::$fieldTagName,
                    'msg' => self::$fieldMsg,
                ),
                'optional' => array (
                    'msg_type' => self::$fieldMsgType,
                    'msg_expires' => self::$fieldMsgExpires,
                    'deploy_status' => self::$fieldDeployStatus,
                    'send_time' => self::$fieldSendTime,
                ),
                'before' => 'verifyGroup',
            ),
            'pushToSmartTag' => array (
                'url' => '/push/tags',
                'required' => array (
                    'type' => self::$fieldGroupType,
                    'selector' => self::$fieldGroupSelector,
                    'msg' => self::$fieldMsg,
                ),
                'optional' => array (
                    'msg_type' => self::$fieldMsgType,
                    'msg_expires' => self::$fieldMsgExpires,
                    'deploy_status' => self::$fieldDeployStatus,
                    'send_time' => self::$fieldSendTime,
                ),
                'before' => 'verifyGroup',
            ),
            'pushBatchUniMsg' => array (
                'url' => '/push/batch_device',
                'required' => array (
                    'channel_ids' => self::$fieldChannelIdList,
                    'msg' => self::$fieldMsg,
                ),
                'optional' => array (
                    'msg_type' => self::$fieldMsgType,
                    'msg_expires' => self::$fieldMsgExpires,
                    'deploy_status' => self::$fieldDeployStatus,
                    'topic_id' => self::$fieldMsgTopic,
                ),
                'before' => 'verifyChannelIds',
            ),
            'queryMsgStatus' => array (
                'url' => '/report/query_msg_status',
                'required' => array (
                    'msg_id' => self::$fieldIdOrList,
                ),
                'optional' => array(
                    'statistic_type' => array ( 'type' => 'string'),
                ),
                'before' => 'verifyMsgIds',
            ),
            'queryTimerRecords' => array (
                'url' => '/report/query_timer_records',
                'required' => array (
                    'timer_id' => self::$fieldTimerId,
                ),
                'optional' => array (
                    'start' => self::$fieldPageStart,
                    'limit' => self::$fieldPageLimit,
                    'range_start' => self::$fieldTimestamp,
                    'range_end' => self::$fieldTimestamp,
                ),
            ),
            'queryTopicRecords' => array (
                'url' => '/report/query_topic_records',
                'required' => array (
                    'topic_id' => self::$fieldMsgTopic,
                ),
                'optional' => array (
                    'start' => self::$fieldPageStart,
                    'limit' => self::$fieldPageLimit,
                    'range_start' => self::$fieldTimestamp,
                    'range_end' => self::$fieldTimestamp,
                ),
            ),
            'queryTimerList' => array (
                'url' => '/timer/query_list',
                'required' => array (),
                'optional' => array (
                    'timer_id' => self::$fieldTimerId,
                    'start' => self::$fieldPageStart,
                    'limit' => self::$fieldPageLimit,
                ),
            ),
            'createTag' => array (
                'url' => '/app/create_tag',
                'required' => array (
                    'tag' => self::$fieldTagName,
                ),
            ),
            'deleteTag' => array (
                'url' => '/app/del_tag',
                'required' => array (
                    'tag' => self::$fieldTagName,
                ),
            ),
            'queryTags' => array (
                'url' => '/app/query_tags',
                'required' => array (),
                'optional' => array (
                    'tag' => self::$fieldTagName,
                     'start' => self::$fieldPageStart,
                    'limit' => self::$fieldPageLimit,
                ),
            ),
            'addDevicesToTag' => array (
                'url' => '/tag/add_devices',
                'required' => array (
                    'tag' => self::$fieldTagName,
                    'channel_ids' => self::$fieldChannelIdList,
                ),
                'before' => 'verifyChannelIds',
            ),
            'delDevicesFromTag' => array (
                'url' => '/tag/del_devices',
                'required' => array (
                    'tag' => self::$fieldTagName,
                    'channel_ids' => self::$fieldChannelIdList,
                ),
                'before' => 'verifyChannelIds',
            ),
            'queryDeviceNumInTag' => array (
                'url' => '/tag/device_num',
                'required' => array (
                    'tag' => self::$fieldTagName,
                ),
            ),
            'queryMessageHistory' => array (
                'url' => '/app/query_msg_history',
                'required' => array (),
                'optional' => array (
                    'msg_id' => self::$fieldIdOrList, 
                    'topic_id' => self::$fieldMsgTopic, 
                    'timer_id' => self::$fieldTimerId, 
                    'push_from' => self::$fieldNumber, 
                    'query_str' => array ( 'type' => 'string'), 
                    'send_time_type' => self::$fieldNumber, 
                    'msg_type' => self::$fieldNumber, 
                    'start' => self::$fieldPageStart, 
                    'limit' => self::$fieldPageLimit 
                ),
                'before' => 'verifyMsgIds',
            ),
            'queryStatisticTopic' => array (
                'url' => '/report/statistic_topic',
                'required' => array (
                    'topic_id' => self::$fieldMsgTopic, 
                ),
                'optional' => array (
                ),
            ),
            'queryStatisticMsg' => array (
                'url' => '/report/statistic_msg',
                'required' => array (),
                'optional' => array (
                    'query_type' => array ( 'type' => 'array'), 
                ),
                'before' => 'verifyRangeTypes',
            ),
            'queryStatisticDevice' => array (
                'url' => '/report/statistic_device',
                'required' => array (),
            ),
            'queryTopicList' => array (
                'url' => '/topic/query_list',
                'required' => array (),
            ),
        );
        
        return $apiMapping;
    }
    
    /**
     * Constructor
     *
     * @param string $apiKey
     *        开发者apikey, 由开发者中心(http://developer.baidu.com)获取
     * @param string $secretKey
     *        开发者当前secretKey, 在应用重新生成secret key后, 旧的secret key将失效, 由开发者中心(http://developer.baidu.com)获取.
     * @param array $curlopts
     *        用于cUrl::curl_setopt方法的控制参数.
     * @link http://php.net/manual/zh/function.curl-setopt.php (curl_setopt相关内容)
     */
    function __construct($apiKey = null, $secretKey = null, $curlopts = array()) {
        
        if($apiKey !== null && $secretKey !== null){
            $this -> setApiKey($apiKey);
            $this -> setSecretKey($secretKey);
        }else if($apiKey !== null || $secretKey !== null){
            $loss = $apiKey == null ? 'apikey' : 'secretKey';
            throw new Exception("need $loss.");
        }else{
            $this -> setApiKey(BAIDU_PUSH_CONFIG::default_apiKey);
            $this -> setSecretKey(BAIDU_PUSH_CONFIG::default_secretkey);
        }
        
        parent::__construct($curlopts);
        $this -> log -> log("SDK ready to work !!");
    }
    
    /**
     * 自动调用已配置的restApi方法.
     *
     * @param string $name        
     * @param array $args        
     * @throws ErrorException
     * @return mixed
     */
    function __call($name, $originArgs) {
        $className = __CLASS__;
        
        $apiMapping = $this -> getMapping(); 
        
        if (! array_key_exists($name, $apiMapping)) {
            throw new ErrorException("Call to undefined method $className::$name()");
        }
        
        $methodDef = $apiMapping [$name];
        
        $requiredDef = $methodDef ['required'];
        $optionalDef = array_key_exists('optional', $methodDef) ? $methodDef ['optional'] : null;
        
        // 取得参数列表.
        $keynames = array_keys($requiredDef);
        
        $realArgsLen = count($originArgs); // 实际参数个数
        $requireArgsLen = count($keynames); // 必要参数个数
        
        $opts = null; // 可选参数;
        $args = $originArgs; // 必要参数;
                             
        // 验证一次参数长度
        switch ($realArgsLen - count($keynames)) {
            case 0 :
                // this is good;
                break;
            case 1 :
                
                // have the $opts, take it out!
                if ($optionalDef != null) {
                    $opts = array_pop($args);
                    break;
                }
            default :
                
                // other case throw error;
                $this -> onError(null, 3, "SDK params invalid, check length of arguments, Need: $requireArgsLen Found: $realArgsLen");
                return false;
        }
        
        $arguments = array();
        
        // 合并, 便于验证时快速取值.
        if($requireArgsLen > 0 ){
            $arguments = array_combine($keynames, $args);
        }
        
        $payload = $this -> newApiQueryTpl(); // 实际的http参数;
                                            
        // 必要参数验证;
        foreach ( $requiredDef as $key => $condition ) {
            $value = $arguments [$key];
            if ($this -> assert -> makesure($value, $condition)) {
                $payload [$key] = $value;
            } else {
                $this -> onError(null, 3, "SDK params invalid, check the param [$key] is " . print_r($value,true));
                return false;
            }
        }
        
        // 验证可选参数
        if (is_array($opts)) {
            foreach ( $optionalDef as $key => $condition ) {
                // 可选参数,仅在设置时才进行验证, 否则直接忽略. 同时这里将忽略多余和不可识别内容.
                if (array_key_exists($key, $opts)) {
                    $value = $opts [$key];
                    if ($this -> assert -> makesure($value, $condition)) {
                        $payload [$key] = $value;
                    } else {
                        $assertErrorMsg = $this -> assert ->lastFailed;
                        $this -> onError(null, 3, "SDK params invalid, $assertErrorMsg, check the param [$key]:" . print_r($value,true));
                        return false;
                    }
                }
            }
        }
        
        //
        $before = array_key_exists('before', $methodDef) ? $methodDef ['before'] : 'none';
        
        if (method_exists($this, $before)) {
            if (call_user_func_array(array (
                $this,
                $before,
            ), array (
                &$payload,
            ))) {
                return $this -> sendRequest($methodDef ['url'], $payload);
            }
        } else {
            $this -> onError(null, 2, "SDK running error, Missing the prepositive method [$before];");
        }
        
        return false;
    }
    
    /**
     * do nothing;
     * 
     * @return boolean
     */
    private function none() {
        return true;
    }
    /**
     * 验证一个http请求参数中的msg内容是否正确
     * @param array &$payload
     * @return boolean
     */
    protected function verifyMessage(&$payload) {
        
        if (is_array($payload ['msg'])) {
            $payload ['msg'] = json_encode($payload ['msg']);
        }
        
        if (array_key_exists('send_time', $payload)) {
            if ($payload ['send_time'] < time() + 60) {
                $this -> onError(null, 3, "SDK params invalid, [send_time] must be greater than the current time + 60 seconds");
                return false;
            }
        }
        
        return true;
    }
    /**
     * 验证一个组播API的http请求参数中的是否正确
     * @param array $payload
     * @return boolean
     */
    protected function verifyGroup(&$payload){
        
        // 消息格式如果错误不继续.
        if(!$this->verifyMessage($payload)){
            // 错误信息应有verifyMessage中生成.
            
            return false;
        }
            
        // 没有type,认为是push/tags的简单调用方式, 需要将type置为1
        $payload['type'] = array_key_exists('type', $payload) ? $payload['type'] : 1;
        
        if($payload['type']  === 1){
            // 必须要求有tag.
            if(!array_key_exists('tag', $payload)){
                $this->onError(null,3,'SDK params invalid, [tag] is required,  when the [type] not 2 ~ 6');
                return false;
            }
        }
        // type不等于1, 必须有selector
        else if(array_key_exists('selector', $payload)){             

            if(is_array($payload['selector'])){
                $payload['selector'] = json_encode($payload['selector']);
            }
            
        }
        // 其它情况,直接认为错误.
        else{
            $this->onError(null,3,'SDK params invalid, [selector] is required,  when the [type] between 2 and 6');
            return false;
        }
        
        return true;
    }
    /**
     * 验证一个API请求中的channleIds是否正确
     * @param array $payload
     * @return boolean
     */
    protected function verifyChannelIds(&$payload){
        
        if(array_key_exists('msg', $payload)){
            // 消息格式如果错误不继续.
            if(!$this->verifyMessage($payload)){
                // 错误信息应有verifyMessage中生成.
                return false;
            }
        }
        
        if(is_array($payload['channel_ids'])){
            $payload['channel_ids'] = json_encode($payload['channel_ids']);
        }
        
        return true;
    }
    /**
     * 验证一个API请求中的msgIds是否正确
     * @param array $payload
     * @return boolean
     */
    protected function verifyMsgIds(&$payload){
        
        if(isset($payload['msg_id']) && is_array($payload['msg_id'])){
            $payload['msg_id'] = json_encode($payload['msg_id']);
        }
        
        return true;
    }
    /**
     * 验证一个API请求中的range_types是否正确
     * @param array $payload
     * @return boolean
     */
    protected function verifyRangeTypes(&$payload){
        
        if(isset($payload['query_type']) && is_array($payload['query_type'])){
            $payload['query_type'] = json_encode($payload['query_type']);
        }
        
        return true;
    }

}
