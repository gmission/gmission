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
 * @file utils.php
 * @encoding UTF-8
 * 
 * 
 *         @date 2014年12月25日
 *        
 */

class PushUtils {
    /**
     * get the timestamp at current dat start
     *
     * NOTE: the result start at the timezone (GTM +8) 00:00:00, not the GTM 0.
     *
     * @param
     *        {number} offset, offset of timezone;
     * @return number
     */
    public static function getDayTimestamp($now = null, $offset = 8) {
        $now = $now === null ? time() : $now;
        
        $gtm0 = $now - ($now % 86400); // GTM 0
        
        $dayline = ($now - $gtm0) / 3600;
        
        // 时差跨天
        if ($dayline + $offset > 23) {
            return $gtm0 + 86400 + $offset * 3600 * - 1;
        } else {
            return $gtm0 + $offset * 3600 * - 1;
        }
    }
    /**
     * get the timestamp at current hour start
     * @param int $num 指定时间
     * @return number
     */
    public static function getHourTimestamp($now = null) {
        $now = $now === null ? time() : $now;
        $diff = $now % 3600; // 1 * 60 * 60;
        return $now - $diff;
    }
    /**
     * get the timestamp at current minute start
     * @param int $num 指定时间
     * @return number
     */
    public static function getMinuteTimestamp($now = null) {
        $now = $now === null ? time() : $now;
        $diff = $now % 60;
        return $now - $diff;
    }
}

