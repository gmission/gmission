<?php
/**
 * *************************************************************************
 *
 * Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
 *
 * ************************************************************************
 */
/**
 *
 * Packing the cUrl and make it easy
 *
 * @file HttpRequest.php
 * @encoding UTF-8
 * 
 * 
 *         @date 2014年12月25日
 *        
 */

require_once(PUSH_SDK_HOME.'/lib/PushSimpleLog.php');
require_once(PUSH_SDK_HOME.'/lib/PushException.php');

class HttpRequest {
    const HTTP_GET = 'GET';
    const HTTP_POST = 'POST';
    /**
     * @var PushSimpleLog
     */
    private $log = null;
    private $urlBase;
    private static $defaultOpts = array (
        
        // default use the http version 1.0 , To prevent on the MAC platform using post speed too slow
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_0,
        CURLOPT_FAILONERROR => false,
        CURLOPT_HEADER => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_HTTPHEADER => array (
             // server端 ,目前唯一支持编码格式,即为utf-8;
            'Content-type: application/x-www-form-urlencoded;charset=utf-8', 
        ),
    );
    
    private $currentOpts = array();
    /**
     * Constructor
     *
     * @param string $urlBase
     *        url基础路径
     * @param array $opts
     *        cUrl options
     * @param PushSimpleLog $log
     * @throws Exception
     */
    function __construct($urlBase = null, $opts = array(), $log = null) {
        
        // 如果未指定, 则创建一个被disable掉的log对象;
        $this -> log = $log === null ? new PushSimpleLog() : $log;
        
        if (! is_callable('curl_version')) {
            throw new Exception("php extension [cUrl] is not exists!!");
        }
        
        if ($urlBase === null) {
            throw new HttpException('URL must be a string');
        }
        
        if (preg_match('/^http.*/i', $urlBase) === 0) {
            throw new HttpException('URL is not correct');
        }
        
        if (strrpos($urlBase, '/') != strlen($urlBase) - 1) {
            $urlBase .= '/';
        }
        
        $this -> urlBase = $urlBase;
        
        if(defined(CURLOPT_IPRESOLVE)){
            self::$defaultOpts[CURLOPT_IPRESOLVE] = CURL_IPRESOLVE_V4;
        }
        
        $this -> currentOpts = self::$defaultOpts;
        
        if (is_array($opts)) {
            foreach ( $opts as $k => $v ) {
                $this -> currentOpts [$k] = $v;
            }
        }
    }
    
    /**
     * 判断一个字符串是否为以http://开头
     *
     * @param string $url
     * @return boolean
     */
    public function isUrlFormat($url){
        return $this->isMatchReg('/^http:\/\/.*/i',$url);
    }
    
    /**
     * 判断一个字符串,是否符合给写的格式
     *
     * @param string $match 正则表达式格式字符串  PREG库风格
     * @param string $str  将验证的字符串
     * @return boolean
     */
    function isMatchReg($match,$str){
        return preg_match($match,$str) > 0;
    }
    /**
     * 以标准uri风格编码一个array<K,V>
     * 
     * @param array<K,V> $body
     * @return string
     */
    private function encodePostBody($body) {
        if ($body === null) {
            return '';
        }
        
        if (! is_array($body)) {
            return urlencode(strval($body));
        }
        
        $result = array ();
        foreach ( $body as $k => $v ) {
            $result [ ] = urlencode($k) . '=' . urlencode($v);
        }
        
        return join('&', $result);
    }
    /**
     * 解析curl的response,并折分其中的header与body部份.
     * @param string $content
     * @return array
     */
    private function parseResponse($content) {
        
        list ( $headerStr, $body ) = explode("\r\n\r\n", $content, 2);
        
        $header = array ();
        
        $headerPart = explode("\r\n", $headerStr);
        
        list ( $httpProtocol, $statusCode, $statStr ) = explode(' ', array_shift($headerPart), 3);
        
        foreach ( $headerPart as $item ) {
            list ( $key, $value ) = explode(':', $item);
            $header [$key] = $value;
        }
        
        $result = array (
            'protocol' => $httpProtocol,
            'status' => intval($statusCode),
            'statusMsg' => $statStr,
            'header' => $header,
            'content' => $body, 
        );
        
        return $result;
    }
    /**
     * 发起http请求, 并返回响应内容
     *
     * @param [string] $path
     *        url的拼接部份,将拼接到urlBase部份
     * @param [string] $method
     *        使用的http请求方法, 目前只支持GET和POST
     * @param [mixed] $payload
     *        请求时的附加的数据.
     * @param [array] $reqHeaders
     *        请求时附加的header信息
     * @param [array] $curlOpts
     *        每次请求时, 对curl的配置信息.
     * @throws HttpException 请求异常时, 抛出异常
     * @return array http response信息 , 具有如下结构 array(
     *         httpProtocol:'',
     *         status:'',
     *         statusMsg:'',
     *         header:array(),
     *         content:""
     *         )
     */
    function request($path = '', $method = "GET", $payload = "", $reqHeaders = null, $curlOpts = null) {
        if ($path === null) {
            throw new HttpException('path must be string');
        }
            
        // 决定访问位置 
        $url = $this->resolve($path);
        
        $curlOptsFinal = $this -> currentOpts;
        
        if (is_array($curlOpts)) {
            foreach ( $curlOpts as $k => $v ) {
                $curlOptsFinal [$k] = $v;
            }
        }
        
        if (is_array($reqHeaders)) {
            if(!is_array($curlOptsFinal [CURLOPT_HTTPHEADER])){
                $curlOptsFinal [CURLOPT_HTTPHEADER] = array(); // 这玩意必须是个数组.不是就直接覆盖.
            }
            $curlOptsFinal [CURLOPT_HTTPHEADER] = array_merge($curlOptsFinal [CURLOPT_HTTPHEADER], $reqHeaders);
            
            //print_r($curlOptsFinal);
        }
        
        $port = parse_url($url, PHP_URL_PORT);
        
        $curlOptsFinal [CURLOPT_URL] = $url;
        
        $curlOptsFinal [CURLOPT_PORT] = empty($port) ? 80 : $port;
        
        $req = curl_init();
        
        curl_setopt_array($req, $curlOptsFinal);
        
        switch ($method) {
            case self::HTTP_GET :
                curl_setopt($req, CURLOPT_CUSTOMREQUEST, 'GET');
                break;
            case self::HTTP_POST :
                curl_setopt($req, CURLOPT_POST, true);
                curl_setopt($req, CURLOPT_POSTFIELDS, $payload);
                break;
            default :
                throw new HttpException("method not be support");
        }
        
        
        $response = curl_exec($req);
        $errCode = curl_errno($req);
        
        
        if ($errCode === 0) {
            curl_close($req);
            // log http access
            $response = $this -> parseResponse($response);
            $status = $response['status'];
            $this -> log -> log("HttpRequest: $status $method $url");
            
            return $response;
        } else {
            // get message and close curl resource;
            
            $errMsg = curl_error($req);
            curl_close($req);
             
            throw new HttpException( "curl_error($errMsg); with url($url)", $errCode);
        }
    }
    /**
     * 快速发起get请求
     * 
     * @param string $path
     *        请求资源路径
     * @param array $query
     *        请求参数
     * @param array $headers
     *        附带header
     * @param array $curlOpts
     *        附加curlOpts
     *        
     * @return array http response信息 , 具有如下结构 array(
     *         httpProtocol:'',
     *         status:'',
     *         statusMsg:'',
     *         header:array(),
     *         content:""
     *         )
     */
    function get($path, $query = null, $headers = null, $curlOpts = null) {
        $payload = $this -> encodePostBody($query);
        
        if ($payload !== "") {
            if (strpos($path, '?')) {
                $url = $path . "&" . $payload;
            } else {
                $url = $path . "?" . $payload;
            }
        }else{
            $url = $path;
        }
        
        return $this -> request($url, self::HTTP_GET, '', $headers, $curlOpts);
    }
    /**
     * 快速发起post请求
     *
     * @param string $path
     *        请求资源路径
     * @param array $postBody
     *        请求参数
     * @param array $headers
     *        附带header
     * @param array $curlOpts
     *        附加curlOpts
     *        
     * @return array http response信息 , 具有如下结构 array(
     *         httpProtocol:'',
     *         status:'',
     *         statusMsg:'',
     *         header:array(),
     *         content:""
     *         )
     */
    function post($path = null, $postBody = null, $headers = null, $curlOpts = null) {
        $payload = $this -> encodePostBody($postBody);
        $this -> log -> debug("\n\n ====== Dump the payload before Http POST send! ====== \n\n$payload\n\n====== End Dump! ======\n");
        return $this -> request($path, self::HTTP_POST, $payload, $headers, $curlOpts);
    }
    
    /**
     * 根据传入内容,决定具体请求地址;
     * @param string $path
     * @return Ambigous <string, unknown>
     */
    public function resolve($path){
        // 如果不指定完整的url, 则认为是访问$urlBase内资源
        if ($this -> isUrlFormat($path)) {
            $url = $path;
        }
        // 忽略重复的路径分隔符
        else if (strpos($path, '/') === 0) {
            $url = $this -> urlBase . substr($path, 1);
        } else {
            $url = $this -> urlBase . $path;
        }
        
        return $url;
    }
    
    /**
     * 取得url中表示资源位置的部份,即去掉query_string及其后的部份
     * 
     * @param string $url
     * @return string
     */
    public function getResourceAddress($url){
        $url = $this->resolve($url);
        
        $p = strpos($url,'?');
        $p = $p === false ? strpos($url,'#') : $p;
        
        return $p === false ? $url : substr($url, 0, $p);
    }
}
