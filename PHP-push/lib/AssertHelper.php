<?php
/***************************************************************************
 * 
 * Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
 * 
 **************************************************************************/
/**
 * 
 * @file AssertHelper.php
 * @encoding UTF-8
 * 
 * @date 2014年12月31日
 *
 */

/**
 * 断言一个值是否符合指定条件
 */
class AssertHelper {
    private $lastFailed = false;
    
    /**
     * 可以组合使用的方法名称列表
     * @var array<string>
     */
    private $checkName = array (
        'type',
        'moreThat',
        'lessThat',
        'between',
        'match',
        'equal',
        'equalStrict',
        'maybe',
        'not',
    );
    
    public function __call($name, $args) {
        if($rs = call_user_func_array(array($this,$name), $args)){
            $this -> lastFailed = false;
        }else{
            $this -> lastFailed = "assert check failed, [$name] return false";
        }
        return $rs;
    }
    
    public function __get($name){
        if($name == 'lastFailed'){
            return $this -> lastFailed;
        }
    }
    
    /**
     * 检查变量类型是否为指定类型;
     *
     * @param mixed $value        
     * @param string | array $type
     * 
     * @return boolean
     */
    private function type($value, $type) {
        
        switch (func_num_args()) {
            case 0 :
            case 1 :
                return false;
            case 2 :
                // 二个参数时, 才执行正常处理逻辑
                
                if (is_array($type)) {
                    foreach ( $type as $t ) {
                        if ($this -> type($value, $t)) {
                            return true;
                        }
                    }
                    return false;
                }
                
                $t = strtolower(gettype($value));
                $type = strtolower($type);
                
                if ($type == $t) {
                    return true;
                } else if ($type == 'mixed') {
                    return true;
                } else {
                    switch ($t) {
                        case "integer" :
                            if ($type == 'int') {
                                return true;
                            }
                        case "double" :
                            return $type == 'number';
                        case "boolean" :
                            return $type == 'bool';
                        case "user function" :
                            return $type == 'function';
                        case "string" :
                        case "array" :
                        case "object" :
                        case "resource" :
                        case "null" :
                        case "unknown type" :
                        default :
                            return false;
                    }
                }
                return false;
            default :
                // 多于两个参数,认为第二个及其后的统统为可能的值.
                $varList = func_get_args();
                $value = array_shift($varList);
                
                return $this -> type($value, $varList);
        }
    
    }
    
    /**
     *
     * 断言一个值大于另一个值
     *
     * @param int $value
     * @param int $checkValue
     * @return boolean
    */
    private function moreThat($value, $checkValue){
        return $value > $checkValue;
    }

    /**
     *
     * 断言一个值小于另一个值
     *
     * @param int $value
     * @param int $checkValue
     * @return boolean
     */
    private function lessThat($value, $checkValue){
        return $value < $checkValue;
    }
    /**
     * 断言一个数值在另外两个数值之间
     * @param int $value
     * @param int $min
     * @param int $max
     * @return boolean
     */
    private function between($value, $min = null, $max = null) {

        $value = intval($value);

        if ($min !== null && $max !== null) {
            return $value >= intval($min) && $value <= intval($max);
        }

        if ($min !== null) {
            return intval($min) <= $value;
        }

        if ($max !== null) {
            return $value <= intval($max);
        }
        return false;
    }
    /**
     * 断言一个字符串匹配指定的正则表达式格式
     *
     * @param string $value
     * @param regexpString $regStr
     * @return boolean
     */
    private function match($value, $regStr) {
        return $this -> type($value, 'string', 'number') && ($this -> equal($value, $regStr) || (preg_match(strval($regStr), strval($value)) > 0));
    }
    /**
     * 断言两个值相等
     * @param mixed $value
     * @param mixed $checkValue
     * @return boolean
     */
    private function equal($value, $checkValue) {
        return $value == $checkValue;
    }
    /**
     * 断言两个值严格相等
     * @param mixed $value
     * @param mixed $checkValue
     * @return boolean
     */
    private function equalStrict($value, $checkValue) {
        return $value === $checkValue;
    }
    /**
     * 断言不等于或非
     * 
     * @param mixed $value        
     * @param mixed $checkValue
     * @return boolean        
     */
    private function not($value) {
        switch (func_num_args()) {
            case 0 :
                return true;
            case 1 :
                return ! $value;
            case 2 :
                $varList = func_get_arg(1);
                
                if (is_array($varList)) {
                    return $this -> not($this -> maybe($value, $varList));
                }
                
                return $value == $varList;
            default :
                $varList = func_get_args();
                $value = array_shift($varList);
                
                return $this -> not($this -> maybe($value, $varList));
        }
    }
    /**
     * 断言一个值在给定的一组值之中. 如果只给定一个非数组的值, 那么则进行equal判断;
     *
     * @param mixed $value
     * @param mixed $varList
     * @return boolean
     */
    private function maybe($value, $varList) {
        switch(func_num_args()){
            case 0:
                return false;
            case 1:
                return !!$value;
            case 2:
                if (is_array($varList)) {
                    return array_search($value, $varList, true) !== false;
                }
                return $value == $varList;
            default:
                $varList = func_get_args();
                $value = array_shift($varList);
                return $this->maybe($value, $varList);
        }
    }
    /**
     * 断言一个值会符合一组条件中的任意一项.
     * @param unknown $value
     * @param unknown $condition
     * @return boolean
     */
    private function possible($value,$conditions = true){
        switch(func_num_args()){
            case 0:
                return false;
            case 1:
                return !!$value;
            case 2:
                if (is_array($conditions)) {
                    $notInAssert = true;
                    foreach ( $conditions as $type => $checkValue ) {
                        if ($this -> maybe($type, $this -> checkName)) {
                            
                            // mark the process type
                            $notInAssert = $notInAssert || true;
                            
                            if (is_array($checkValue)) {
                                array_unshift($checkValue, $value);
                            } else {
                                $checkValue = array (
                                    $value,
                                    $checkValue, 
                                );
                            }
                            
                            // call other assert, if true return else continue;
                            if (call_user_func_array(array (
                                $this,
                                $type, 
                            ), $checkValue)) {
                                return true;
                            }
                        }
                    }
                    
                    // 如果未进行过assert判断,则进行value search
                    return $notInAssert ? $this -> maybe($value, $conditions) : false;
                }
        
                return $value == $conditions;
                
            default:
                $conditions = func_get_args();
                $value = array_shift($conditions);
                
                foreach ($conditions as $c){
                    if($this->possible($value, $c)){
                        return true;
                    }
                }
                
                // 如果未进行过assert判断,则进行value search
                return $this->maybe($value, $conditions);
        }
    }
    /**
     * 判断一个值是否完全符合一组条件
     * @param mixed $value
     * @param array $conditions
     * @return boolean
     */
    private function makesure($value, $conditions = false) {
        switch (func_num_args()) {
            case 0 :
                return false;
            case 1 :
                return ! ! $value;
            case 2 :
                if (is_array($conditions)) {
                    
                    // 必须全部返回true, 结果才能为true; 任意false结果为false
                    foreach ( $conditions as $type => $checkValue ) {
                        
                        // 可以调用断言
                        if ($this -> maybe($type, $this -> checkName)) {
                            // print_r($type);
                            // print_r($conditions);
                            if (is_array($checkValue)) {
                                array_unshift($checkValue, $value);
                            } else {
                                $checkValue = array (
                                    $value,
                                    $checkValue,
                                );
                            }
                            
                            // call other assert, if true return else continue;
                            if (! call_user_func_array(array (
                                $this,
                                $type,
                            ), $checkValue)) {
                                return false;
                            }
                        } else {
                            
                            // 如果任意值不能调用assert判断, 直接判断值相等.. 如果不等, 直接返回false
                            if ($value !== $type) {
                                return false;
                            }
                        }
                    
                    }
                    return true;
                }
                
                return $value == $conditions;
        }
    }
}
 
 