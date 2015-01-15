/**
 * Created by chenzhao on 17/2/14.
 */


//
//var gmissionServices = lib.module('gmissionService', ['ngResource']);
//
//gmissionServices.factory('Phone', ['$resource',
//  function($resource){
//    return $resource('phones/:phoneId.json', {}, {
//      query: {method:'GET', params:{phoneId:'phones'}, isArray:true}
//    });
//  }]);
//
//var addAutoAPIAsService = function(modelName){
//    gmissionServices.factory(modelName, ['$resource', function($resource){
//        return $resource(modelName+'/:id', {}, {
//            query: {method:'GET', params:{id:modelName}, isArray:false}
//        });
//    }])
//}
