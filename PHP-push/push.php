<?php
/**
 * Created by PhpStorm.
 * User: haidaoxiaofei
 * Date: 07/04/16
 * Time: 4:41 PM
 */

require_once 'sdk.php';

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


//push message to android devices
function pushMessage_android($channel_id, $message)
{
    $apiKey = 'OLYzDQA0lCtvhxR8VKPoE19D';
    $secretkey = 'rUsfEY9sHrqpzqFVENqmoSyffpKMyUSc';
    $sdk = new PushSDK($apiKey, $secretkey);

    $opts = array (
        'msg_type' => 0, //1 means notifications，0 means messages
        'device_type' => 3
    );

    $rs = $sdk -> pushMsgToSingleDevice($channel_id, $message, $opts);


    if ( $rs == false)
    {
        error_output ( 'WRONG, ' . __FUNCTION__ . ' ERROR!!!!!' ) ;
        error_output ( 'ERROR NUMBER: ' . $sdk->getLastErrorCode() ) ;
        error_output ( 'ERROR MESSAGE: ' . $sdk->getLastErrorMsg() ) ;
        error_output ( 'REQUEST ID: ' . $sdk -> getRequestId() );
    }
    else
    {
        right_output ( 'SUCC, ' . __FUNCTION__ . ' OK!!!!!' ) ;
        right_output ( 'result: ' . print_r ( $rs, true ) ) ;
    }
}


//push message to ios devices

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


function pushMessage_ios ($channel_id, $message, $deploy_status)
{
    $apiKey = 'LQpGHpuTYA0lkjQj6zY3ZVfB';
    $secretkey = 'kkwpcFMTsKhdECYMbEOl7NF1hG2OGd4x';
    $sdk = new PushSDK($apiKey, $secretkey);

    $opts = array (
        'msg_type' => 0, //1 means notifications，0 means messages
        'deploy_status' => $deploy_status,   // iOS App deployment status :  1：development；2：production； if not configured, default is production
        'device_type' => 4
    );

    $rs = $sdk -> pushMsgToSingleDevice($channel_id, $message, $opts);


    if ( $rs == false)
    {
        error_output ( 'WRONG, ' . __FUNCTION__ . ' ERROR!!!!!' ) ;
        error_output ( 'ERROR NUMBER: ' . $sdk->getLastErrorCode() ) ;
        error_output ( 'ERROR MESSAGE: ' . $sdk->getLastErrorMsg() ) ;
        error_output ( 'REQUEST ID: ' . $sdk -> getRequestId() );
    }
    else
    {
        right_output ( 'SUCC, ' . __FUNCTION__ . ' OK!!!!!' ) ;
        right_output ( 'result: ' . print_r ( $rs, true ) ) ;
    }
}




$app = $_REQUEST['app'];

$platform = $_REQUEST['platform'];

$channel_id = $_REQUEST['channel_id'];

$message = $_REQUEST['message'];

$deployStatus = $_REQUEST['deploy_status'];


if ($platform=='android'){
    pushMessage_android($channel_id, $message);
}else if ($platform=='ios'){
    if ($deployStatus=='production'){
        pushMessage_ios_production($channel_id, $message);
    }else if ($deployStatus=='developing'){
        pushMessage_ios_developing($channel_id, $message);
    }else if ($deployStatus=='both'){
        pushMessage_ios_developing($channel_id, $message);
        pushMessage_ios_production($channel_id, $message);
    }else{
        pushMessage_ios_developing($channel_id, $message);
    }

}else{
    error_output ('INVALID PARAMETERS!');
}






















