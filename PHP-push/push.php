<?php
/**
 * Created by PhpStorm.
 * User: chenzhao
 * Date: 4/11/14
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


//推送android设备消息
function pushMessage_android($channel_id, $message)
{
    $sdk = new PushSDK();

    $opts = array (
        'msg_type' => 0, //1表示通知，0表示透传
        'device_type' => 3
    );

    // 向目标设备发送一条消息
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


function pushMessage_ios ($channel_id, $message, $deploy_status)
{
    $sdk = new PushSDK();

//    $message = array (
//        'aps' => array (
//            // 消息内容
//            'alert' => "hello, this message from baidu push service.",
//        ),
//    );

    $opts = array (
        'msg_type' => 0, //1表示通知，0表示透传
        'deploy_status' => $deploy_status,   // iOS应用的部署状态:  1：开发状态；2：生产状态； 若不指定，则默认设置为生产状态。
        'device_type' => 4
    );

    // 向目标设备发送一条消息
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






















