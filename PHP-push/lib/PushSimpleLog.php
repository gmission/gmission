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
 * @file SimpleLog.php
 * @encoding UTF-8
 *
 * 
 *         @date 2014年12月25日
 *        
 */
class PushSimpleLog {
    private $out = null;
    private $log_level = 1;
    private $max_level = 3;
    private $prefix = 'PUSH_SDK';
    private $tags = array (
        'DEV',
        'INFO',
        'WARN',
        'FAULT', 
    );
    /**
     * 实际log输出方法
     * 
     * @param mixed $log
     * @param number $level
     * @param string $prefix
     * @return void
     */
    protected function innerWrite($log, $level = 1, $prefix = null) {
        $level = intval($level);
        if(intval($level) < $this->log_level || $this -> out === null){
            return;
        }
        
        $timestamp = time();
        
        $prefix = $prefix === null ? $this->prefix : $prefix;
        
        $tag = $this->tags[$level];
        
        $msg = "[$tag][$timestamp][$prefix] $log; \n";
        
        if (is_callable($this -> out)) {
            $out = $this -> out;
            $out($msg . '<br />');   // if out to page , add the BR, easy to watch 
            return;
        }
        
        fwrite($this -> out, $msg);
    }
    /**
     * 打印一条dev信息
     * @param string $log
     * @param string $prefix
     */
    function dev($log, $prefix = null) {
        $this -> innerWrite($log, 0, $prefix);
    }
    /**
     * 打印一条info信息
     * @param string $log
     * @param string $prefix
     */
    function info($log, $prefix = null) {
        $this -> innerWrite($log, 1, $prefix);
    }
    /**
     * 打印一条warn信息
     * @param string $log
     * @param string $prefix
     */
    function warn($log, $prefix = null) {
        $this -> innerWrite($log, 2, $prefix);
    }
    /**
     * 打印一条fault信息
     * @param string $log
     * @param string $prefix
     */
    function fault($log, $prefix = null) {
        $this -> innerWrite($log, 3, $prefix);
    }
    
    // alias方法
    /**
     * alias: dev
     * @param string $log
     * @param string $prefix
     */
    function debug($log, $prefix = null) {
        $this -> dev($log, $prefix);
    }
    /**
     * alias: info
     * @param string $log
     * @param string $prefix
     */
    function log($log, $prefix = null) {
        $this -> info($log, $prefix);
    }
    /**
     * alias: fault
     * @param string $log
     * @param string $prefix
     */
    function error($log, $prefix = null) {
        $this -> fault($log, $prefix);
    }
    /**
     * alias: fault
     * @param string $log
     * @param string $prefix
     */
    function err($log, $prefix = null) {
        $this -> fault($log, $prefix);
    }
    
    /**
     * Constructor
     * @param string $out 输出位置, 默认为disable即禁用.
     * @param number $level 过滤级别, 0 - 4, 数值越小信息越详细, 4则不打印任何信息
     * @return void
     */
    function __construct($out = 'disable', $level = 1) {
        
        if($level > $this -> max_level){
            $out = 'disable';
        }
        
        switch ($out) {
            case "disable" :
                // just ignore !!
                return;
            case "page" :
                $this -> out = 'print_r';
                break;
            case "stdout" :
                $out = "php://stdout";
                $this -> out = fopen($out, 'w');
                break;
            default :
                // if can not be write , log will be disable!
                if (is_writable($out)) {
                    $this -> out = fopen($out, 'w');
                }
        }
        
        $this->log_level = $level;
        
        $this->log("PushSimpleLog: ready to work!");
    }
    /**
     * __destruct
     */
    function __destruct(){
        @is_resource($this->out) ? fclose($this->out) : $this->out = null;
    }
}