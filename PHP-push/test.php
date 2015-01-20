<?php
/**
 * Created by PhpStorm.
 * User: chenzhao
 * Date: 4/11/14
 * Time: 3:53 PM
 */

phpinfo();

require_once("sample.php");
require_once("push.php");

$userId = '1044981726564561550';

test_pushMessage_android($userId);
test_pushMessage_ios($userId);



$message = '{
			"title": "test_push",
			"description": "open url",
			"notification_basic_style":7,
			"open_type":1,
			"url":"http://www.baidu.com"
 		}';


$messageKey = "msg_key";


pushMessage_android($userId, $message, $messageKey);



$iOSMessage = '{
		"aps":{
			"alert":"msg from baidu push",
			"sound":"",
			"badge":0
		}
 	}';

pushMessage_ios_developing($userId, $iOSMessage);



//test_queryAppIoscert();

echo "test";