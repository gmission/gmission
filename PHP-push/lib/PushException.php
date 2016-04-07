<?php
/***************************************************************************
 * 
 * Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
 * 
 **************************************************************************/
/**
 * 
 * @file PushException.php
 * @encoding UTF-8
 * 
 * @date 2014年12月31日
 *
 */

/**
 * 表示一个服务端API调用异常,接收到这个异常一般表示客户端及网络运行正常
 */
class ServerException extends Exception {
    /**
     * Constructor
     * @param string $msg
     * @param int $code
     */
    function __construct($msg, $code) {
        parent::__construct($msg, $code);
    }
}

/**
 * 表示一个http访问异常,该异常由客户端调用http功能时产生.一般表示网络访问存在异常
 */
class HttpException extends Exception {
    /**
     * Constructor
     * @param string $msg
     * @param int $code
     */
    function __construct($message, $code) {
        parent::__construct($message, $code);
    }
}

/**
 * 表示一个客户端异常, 一般为初始化, 参数检查等出现异常
 */
class ClientException extends Exception {
    /**
     * Constructor
     * @param string $msg
     * @param int $code
     */
    function __construct($message, $code) {
        parent::__construct($message, $code);
    }
}
