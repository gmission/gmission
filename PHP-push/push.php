<?php
/**
 * Created by PhpStorm.
 * User: chenzhao
 * Date: 4/11/14
 * Time: 4:41 PM
 */


require_once("Channel.class.php");

function error_output ( $str )
{
    echo $str . "\n";
    error_log($str, 0);
}

function right_output ( $str )
{
    echo $str . "\n";
    error_log($str, 0);
}


//请开发者设置自己的apiKey与secretKey
$apiKey = "OLYzDQA0lCtvhxR8VKPoE19D";
$secretKey = "rUsfEY9sHrqpzqFVENqmoSyffpKMyUSc";


//推送android设备消息
function pushMessage_android($user_id, $message, $message_key)
{
    global $apiKey;
    global $secretKey;
    $channel = new Channel ( $apiKey, $secretKey ) ;
    //推送消息到某个user，设置push_type = 1;
    //推送消息到一个tag中的全部user，设置push_type = 2;
    //推送消息到该app中的全部user，设置push_type = 3;
    $push_type = 1; //推送单播消息
    $optional[Channel::USER_ID] = $user_id; //如果推送单播消息，需要指定user
    //optional[Channel::TAG_NAME] = "xxxx";  //如果推送tag消息，需要指定tag_name

    //指定发到android设备
    $optional[Channel::DEVICE_TYPE] = 3;
    //指定消息类型为消息（透传给应用的消息体）
    $optional[Channel::MESSAGE_TYPE] = 0;

    $ret = $channel->pushMessage ( $push_type, $message, $message_key, $optional ) ;
    if ( false === $ret )
    {
        error_output ( 'WRONG, ' . __FUNCTION__ . ' ERROR!!!!!' ) ;
        error_output ( 'ERROR NUMBER: ' . $channel->errno ( ) ) ;
        error_output ( 'ERROR MESSAGE: ' . $channel->errmsg ( ) ) ;
        error_output ( 'REQUEST ID: ' . $channel->getRequestId ( ) );
    }
    else
    {
        right_output ( 'SUCC, ' . __FUNCTION__ . ' OK!!!!!' ) ;
        right_output ( 'result: ' . print_r ( $ret, true ) ) ;
    }
}


//推送ios设备消息

function pushMessage_ios_developing($user_id, $message)
{
    $deploy_status = 1;
    pushMessage_ios($user_id, $message, $deploy_status);
}


function pushMessage_ios_production($user_id, $message)
{
    $deploy_status = 2;
    pushMessage_ios($user_id, $message, $deploy_status);
}


function pushMessage_ios ($user_id, $message, $deploy_status)
{
    global $apiKey;
    global $secretKey;
    $channel = new Channel ( $apiKey, $secretKey ) ;

    $push_type = 1; //推送单播消息
    $optional[Channel::USER_ID] = $user_id; //如果推送单播消息，需要指定user

    //指定发到ios设备
    $optional[Channel::DEVICE_TYPE] = 4;
    //指定消息类型为通知
    $optional[Channel::MESSAGE_TYPE] = 1;
    //如果ios应用当前部署状态为开发状态，指定DEPLOY_STATUS为1，默认是生产状态，值为2.
    //旧版本曾采用不同的域名区分部署状态，仍然支持。
    $optional[Channel::DEPLOY_STATUS] = $deploy_status;

    $message_key = "msg_key";
    $ret = $channel->pushMessage ( $push_type, $message, $message_key, $optional ) ;
    if ( false === $ret )
    {
        error_output ( 'WRONG, ' . __FUNCTION__ . ' ERROR!!!!!' ) ;
        error_output ( 'ERROR NUMBER: ' . $channel->errno ( ) ) ;
        error_output ( 'ERROR MESSAGE: ' . $channel->errmsg ( ) ) ;
        error_output ( 'REQUEST ID: ' . $channel->getRequestId ( ) );
    }
    else
    {
        right_output ( 'SUCC, ' . __FUNCTION__ . ' OK!!!!!' ) ;
        right_output ( 'result: ' . print_r ( $ret, true ) ) ;
    }
}




$app = $_REQUEST['app'];

$platform = $_REQUEST['platform'];

$user_id = $_REQUEST['user_id'];

$message = $_REQUEST['message'];

$messageKey = $_REQUEST['message_key'];

$deployStatus = $_REQUEST['deploy_status'];


if ($platform=='android'){
    pushMessage_android($user_id, $message, $messageKey);
}else if ($platform=='ios'){
    if ($deployStatus=='production'){
        pushMessage_ios_production($user_id, $message);
    }else if ($deployStatus=='developing'){
        pushMessage_ios_developing($user_id, $message);
    }else if ($deployStatus=='both'){
        pushMessage_ios_developing($user_id, $message);
        pushMessage_ios_production($user_id, $message);
    }else{
        pushMessage_ios_developing($user_id, $message);
    }

}else{
    error_output ('INVALID PARAMETERS!');
}






















