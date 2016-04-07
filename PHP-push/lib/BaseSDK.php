<?php
/***************************************************************************
 * 
 * Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
 * 
 **************************************************************************/
/**
 * 仅提供最基本的错误控制和初始化参数功能
 * 
 * @file BaseSDK.php
 * @encoding UTF-8
 * 
 * @date 2014年12月29日
 *
 */

require_once(PUSH_SDK_HOME.'/configure.php');

require_once(PUSH_SDK_HOME.'/lib/HttpRequest.php');
require_once(PUSH_SDK_HOME.'/lib/PushException.php');
require_once(PUSH_SDK_HOME.'/lib/PushSimpleLog.php');
require_once PUSH_SDK_HOME . '/lib/AssertHelper.php';

/**
 * 仅提供最基本的错误控制和初始化参数功能
 * 包装最基本的http访问动作, 参数类型定义等
 * 
 *
 */
class BaseSDK{
    /**
     * 版本标识;
     * 
     * @var string
     */
    const CURRENT_VERSION = '3.0.0';
    
    /*
     * 定义异常类型
     */
    const ERR_UNKNOWN = 'Exception';
    const ERR_CLIENT = 'ClientException';
    const ERR_NET = 'HttpException';
    const ERR_SERVER = 'ServerException';
    
    static protected $fieldNumber = array (
        'type' => 'number', 
    );
    
    static protected $fieldIdStr = array (
        'type' => 'string',
        'match' => '/\d{10,25}/', 
    );
    
    static protected $fieldIdOrList = array (
        'type' => array (
            'array', 
            'string' 
        ) 
    );
    
    static protected $fieldTimestamp = array (
        'type' => 'number', 
    );
    
    /**
     * channel_id 验证规则
     *
     * @var array
     */
    static protected $fieldChannelId = array (
        'type' => 'string',
        'match' => '/\d{10,25}/', 
    );
    
    /**
     * 一组channel_id
     * 
     * @var array
     */
    static protected $fieldChannelIdList = array (
        'type' => 'array', 
    );
    
    /**
     * 一条消息的id
     * 
     * @var array
     */
    static protected $fieldMsgId =  array (
        'type' => 'string',
        'match' => '/\d{10,25}/', 
    );
    
    /**
     * 一个定时器的id
     * 
     * @var array
     */
    static protected $fieldTimerId =  array (
        'type' => 'string',
        'match' => '/\d{10,25}/', 
    );
    
    /**
     * record limit
     * 
     * @var array
     */
    static protected $fieldPageLimit = array (
        'between' => array (
            1,
            100, 
        ),
    );
    /**
     * record start
     * 
     * @var array
     */
    static protected $fieldPageStart = array (
        'type' => 'number', 
    );
    
    /**
     * msg
     * 
     * @var array
     */
    static protected $fieldMsg = array (
        'type' => array (
            'string',
            'array', 
        ),
    );
    /**
     * MSG_TYPE 验证规则
     *
     * @var array
     */
    static protected $fieldMsgType = array (
        'maybe' => array (
            0,
            1, 
        ),
    );
    /**
     * MSG_EXPIRES 验证规则
     *
     * @var array
     */
    static protected $fieldMsgExpires = array (
        'between' => array (
            1,
            604800,          // 1 ~ 86400 * 7
        ),
    );
    /**
     * DEPLOY_STATUS 验证规则
     *
     * @var array
     */
    static protected $fieldDeployStatus = array (
        'maybe' => array (
            1,
            2, 
        ),
    );
    /**
     * MSG_TOPIC 验证规则
     *
     * @var array
     */
    static protected $fieldMsgTopic = array (
        'type' => 'string',
        'match' => '/^.{1,128}$/i', 
    );
    /**
     * SEND_TIME 验证规则
     *
     * @var array
     */
    static protected $fieldSendTime = array (
        'type' => 'number', 
    );
    /**
     * TAG_NAME 验证规则
     *
     * @var array
     */
    static protected $fieldTagName = array (
        'type' => 'string',
        'match' => '/^.{1,128}$/', 
    );
    /**
     * GROUP_TYPE 验证规则
     *
     * @var array
     */
    static protected $fieldGroupType = array (
        'between' => array (
            2,
            6, 
        ),
    );
    /**
     * GROUP_SELECTOR 验证规则
     *
     * @var array
     */
    static protected $fieldGroupSelector = array (
        'type' => array (
            'string',
            'array', 
        ),
    );
    // const FIELD_ = array (
    // 'type' => 'number'
    // );
    
    /**
     * 设备类型常量 Android
     * 
     * @var int 3
     */
    const DEVICE_ANDROID = 3;
    /**
     * 设备类型常量 IOS
     * 
     * @var int 4
     */
    const DEVICE_IOS = 4;
    
    /*
     * 错误信息
     */
    protected $errorCode = null;
    protected $errorMsg = '';
    
    /*
     * requireId
     */
    protected $requestId = null;
    
    /**
     * http请求包装
     * 
     * @var HttpRequest
     */
    public $http = null;
    /**
     * 目志输出对象
     * 
     * @var PushSimpleLog
     */
    public $log = null;
    
    /**
     * 断言对象
     * 
     * @var AssertHelper
     */
    public $assert = null;
    
    // 是否抛出异常
    private static $suppressException = false;
    
    // ------ business require ------- //
    
    /**
     * api key of app,
     * you can get it from http://developer.baidu.com
     * 
     * @var string
     */
    protected $apikey = '';
    
    /**
     * secret key of app,
     * you can get it from http://developer.baidu.com.
     * 
     * @var string
     */
    protected $secretKey = '';
    
    /**
     * 指定一个默认的deviceType, 默认为null即不指定,
     * 兼容老版本app时,必须指定一个固定值.
     * 3为android, 4为ios;
     * 
     * @deprecated ;
     * @var int
     */
    protected $deviceType = null;
    
    /**
     * 决定是否携带expires参数, 当值大于0时, 将请求时的expires参数置为 : time() + $signExpires, 否则不携带expires
     * 
     * @var int
     */
    protected $signExpires = 0;
    
    // ======== to prevent modify the value from external ======== //
    
    /**
     * 取得最后一次错误码
     * 
     * @return string
     */
    public function getLastErrorCode() {
        return $this -> errorCode;
    }
    
    /**
     * 取得最后一次错误描述
     * 
     * @return string
     */
    public function getLastErrorMsg() {
        return $this -> errorMsg;
    }
    
    /**
     * 取得最后一次与服务端交互产生的requestId, 无论实际API调用是否成功, requestId都应当存在
     *
     * @return string
     */
    public function getRequestId() {
        return $this -> requestId;
    }
    /**
     * 设置当前使用的apikey
     * 
     * @param string $apiKey        
     */
    public function setApiKey($apiKey) {
        $this -> apikey = $apiKey;
    }
    /**
     * 设置当前使用的secretKey
     * 
     * @param string $secretKey        
     */
    public function setSecretKey($secretKey) {
        $this -> secretKey = $secretKey;
    }
    /**
     * 设置一个默认的deviceType.
     *
     * @deprecated
     *
     * @param string $deviceType        
     */
    public function setDeviceType($deviceType = null) {
        switch ($deviceType) {
            case self::DEVICE_ANDROID :
                $this -> deviceType = self::DEVICE_ANDROID;
                break;
            case self::DEVICE_IOS :
                $this -> deviceType = self::DEVICE_IOS;
                break;
            default :
                $this -> deviceType = null;
        }
    }
     
    /**
     * 记录当前发生的错误内容,供getErrorxxxxx相关接口使用, 同时根据是否抛出异常的配置决定是否生成并抛出一个错误.
     * 
     * @param int $code 错误码, 非0表示有错误发生
     * 
     *                -1 未知错误
     *                 0 表示没有错误  
     *         1 ~   99 clientSDK错误
     *       400 ~   600 网络错误, http status code,  200-300为成功消息, 不可占用.
     *     10000 ~ 20000 服务端错误
     *     
     * @param string $requestId  请求ID, 由服务端生成并返回
     * @param int $code 错误码
     * @param string $msg 错误消息
     * @return Exception
     */
    protected function onError($requestId = null, $code = 0, $msg = ''){

        $this -> errorMsg = $msg;
        $this -> errorCode = $code;
        $this -> requestId = $requestId;
        
        if ($code === 0) {
            // 无错误;
            return null;
        }
        if ($code > 0 && $code < 100) {
            // Http状态应小于100,所以认为小于100的均为SDK内部错误
            $type = self::ERR_CLIENT;
        } else if ($code >= 400 && $code < 600) {
            // 只将Http的错误状态认为是网络错误. 200及300对于当前restApi来说将不能被理解.
            $type = self::ERR_NET;
        } else if ($code >= 10000) {
            // 大于10000应为服务端返回的错误
            $type = self::ERR_SERVER;
        } else {
            $code = - 1;
            $type = self::ERR_UNKNOWN;
        }
        
        // 生产错误
        $err = new $type("[$code] $msg", $code);
        
        if (self::$suppressException) {
            $this -> log -> err($err -> __toString());
            return $err; // 拒绝抛出
        } else {
            throw $err;
        }
     }
     
    // -------  common method ------ //
     
    /**
     * Constructor
     * 
     * @param array $curlOpts 用于内部http包装对象使用的全局curl参数.
     */
    function __construct($curlOpts = array()) {
        date_default_timezone_set('Asia/Shanghai');
        self::$suppressException = BAIDU_PUSH_CONFIG::SUPPRESS_EXCPTION;
        $this -> log = new PushSimpleLog(BAIDU_PUSH_CONFIG::LOG_OUTPUT, BAIDU_PUSH_CONFIG::LOG_LEVEL);
        
        try {
            
            $this -> http = new HttpRequest(BAIDU_PUSH_CONFIG::HOST, $curlOpts, $this -> log);
            $this -> log -> log("HttpRequest: ready to work...");
        
        } catch ( Exception $e ) {
            $this -> log -> fault($e -> __toString());
            die();
        }
        
        $this -> assert = new AssertHelper();
        
        $this -> signExpires = intval(BAIDU_PUSH_CONFIG::SIGN_EXPIRES);
        
        $this -> log -> log("SDK: initializing...");
    }
    
    /**
     * 判断一个字符串是否为以http://开头
     *
     * @param string $url        
     * @return boolean
     */
    public function isUrlFormat($url) {
        return $this -> http -> isUrlFormat($url);
    }
    
    /**
     * 判断一个字符串,是否符合给写的格式
     *
     * @param string $match
     *        正则表达式格式字符串 PREG库风格
     * @param string $str
     *        将验证的字符串
     * @return boolean
     */
    function isMatchReg($match, $str) {
        return $this -> http -> isMatchReg($match, $str);
    }
    
    /**
     * 计算请求迁名
     * 
     * @param string $method
     *        GET|POST
     * @param string $url
     *        请求的完整url, 不含query部份
     * @param array $arrContent
     *        提交的数据项,包含get及post,但不包含签名项
     * @return string
     */
    function genSign($method, $url, $arrContent) {
        
        if ($this -> isMatchReg('/(^get$)|(^post$)/i', $method) === 0) {
            $this -> onError(null, 3, 'SDK: params invalid, $method must be "GET" or "POST"');
            return null;
        }
        
        if (! $this -> isUrlFormat($url)) {
            $this -> onError(null, 3, 'SDK: params invalid, $url is invalid!');
            return null;
        }
        
        $secret_key = $this -> secretKey;
        
        $baseStr = strtoupper($method) . $url;
        
        ksort($arrContent);
        
        foreach ( $arrContent as $key => $value ) {
            $baseStr .= $key . '=' . $value;
        }
        
        $sign = md5(urlencode($baseStr . $secret_key));
        
        return $sign;
    }
    /**
     * 生成携带默认请求的数组对象.
     *
     * @return multitype:number string
     */
    public function newApiQueryTpl() {
        $rs = array (
            'apikey' => $this -> apikey,
            'timestamp' => time(),
        );
        
        if ($this -> deviceType === null && BAIDU_PUSH_CONFIG::default_devicetype !== null) {
            $this->setDeviceType(BAIDU_PUSH_CONFIG::default_devicetype);
        }
        
        if($this -> deviceType !== null ){
            $rs ['device_type'] = $this -> deviceType;
        }
        
        if ($this -> signExpires > 0) {
            $rs ['expires'] = $rs ['timestamp'] + $this -> signExpires;
        }
        
        return $rs;
    }
    
    /**
     * 解析response并判断响应内容是否正确.
     * 如果结果符合restAPI结果格式,则返回结果中包含的response_params内容, 否则依据配置中是不是压制错误产生错误或返回null
     *
     * @param array $response
     *        由httpRequest对象get,post,request等方法返回的结果数组
     * @return mixed|NULL
     */
    public function parse($response) {
        extract($response);
        
        $this -> log -> log("Parse Response: $status, $statusMsg, $content");
        
        $result = json_decode($content, true);
        
        if ($result !== null && array_key_exists('request_id', $result)) {
            
            if ($status == 200) {
                
                if (array_key_exists('response_params', $result)) {
                    // 状态200,并且成功解析出json结果. 表示请求成功
                    $this -> onError($result ['request_id']);
                    return $result ['response_params'];
                } else {
                    // json可以解析, 但是格式不可理解.
                    $this -> onError($result ['request_id'], 4, "http status is ok, but REST returned invalid json struct.");
                }
            
            } else {
                if (array_key_exists('error_code', $result) && array_key_exists('error_msg', $result)) {
                    // 状态不等于200, 但能解析出结果. 表示请求成功, 但是服务端返回错误
                    $this -> onError($result ['request_id'], $result ['error_code'], $result ['error_msg']);
                } else {
                    // json可以解析, 但是格式不可理解.
                    $this -> onError($result ['request_id'], 4, "http status is ok, but REST returned invalid json struct.");
                }
            }
        
        } else {
            
            if ($status == 200) {
                // 无法解析出json, 响应200,
                $this -> onError(null, 4, "http status is ok, but REST returned invalid json string.");
            } else if ($status >= 400) {
                
                // 无法解析出json, 但是响应一个可理解的http错误
                $this -> onError(null, $status, "http response status  : $statusMsg");
            
            } else {
                
                // 响应200-399 , 即除200外任意http成功状态, 均不能被理解, 响应 (-1) 错误.
                $limitContent = strlen($content);
                
                if ($limitContent > 0) {
                    $limitContent = substr($content, 200) . "..." . strlen($content);
                } else {
                    $limitContent = 'Empty';
                }
                
                $this -> onError(null, - 1, "Can not process the http response. with status ($status, $statusMsg), content ($limitContent);");
            }
        }
        return false;
    }
    /**
     * 发送一个rest Api 请求
     * @param string $api 请求地址
     * @param array<K,V> $query 请求参数
     * @param string $method 请求方法 目前只支持 GET, POST
     * @param string $header http header
     * @param string $curlOpts curl选项
     * @return mixed 解析结果,如果失败将返回false, 否则应返回解析后的服务端返回的json数据
     */
    protected function sendRequest($api, $query, $method = "POST", $header=null, $curlOpts = null){
        
        $url = $this->http->getResourceAddress($api);
        
        $query['sign'] = $this -> genSign($method, $url, $query);
        
        if($header == null){
            $header = array('User-Agent: '. $this->makeUA());
        }
        
        if($method == 'GET'){
            $response = $this -> http -> get($api, $query, $header, $curlOpts);
        }else{
            $response = $this -> http -> post($api, $query, $header, $curlOpts);
        }
        
        return $this->parse($response);
    }
    
    protected function makeUA(){

        $sdkVersion = self::CURRENT_VERSION;
        
        $sysName = php_uname('s');
        $sysVersion = php_uname('v');
        $machineName = php_uname('m');
        
        $systemInfo = "$sysName; $sysVersion; $machineName";
        
        $langName = 'PHP';
        $langVersion = phpversion();
        
        $serverName = php_sapi_name();
        $serverVersion = "Unknown";
        
        $sendInfo = 'ZEND/' . zend_version();
        
        $serverInfo = "$serverName/$serverVersion";
        
        if(isset($_SERVER['SERVER_SOFTWARE'])){
            $serverInfo .= '(' . $_SERVER['SERVER_SOFTWARE'] . ')';
        }
        
        
        $tpl = "BCCS_SDK/3.0 ($systemInfo) $langName/$langVersion (Baidu Push SDK for PHP v$sdkVersion) $serverInfo $sendInfo";
        
        return $tpl;
    } 
}

