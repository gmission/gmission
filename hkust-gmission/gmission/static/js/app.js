/**
 * Created by chenzhao on 17/2/14.
 */


var app = angular.module('gmissionApp', ['ngRoute', 'restangular', 'gmissionControllers']);


app.config(function (RestangularProvider) {
    RestangularProvider.setBaseUrl('../../auto-api/');
//  RestangularProvider.setRequestSuffix('');

    RestangularProvider.setResponseExtractor(function (response, operation, what, url) {
//        console.log('setResponseExtractor', response);
        var newResponse;
        if (operation === "getList") {
            newResponse = response.objects;
        } else {
            newResponse = response;
        }
        return newResponse;
    });
});


app.config(function ($routeProvider) {
    $routeProvider.when('/category', {
        templateUrl: './all-category.html',
        controller: 'AllCategoryCtrl'
    }).when('/category/:id', {
        templateUrl: './category.html',
        controller: 'CategoryCtrl'
    }).when('/location/:id', {
        templateUrl: './location.html',
        controller: 'LocationCtrl'
    }).when('/request/:id', {
        templateUrl: './request.html',
        controller: 'RequestCtrl'
    }).when('/messages', {
        templateUrl: './message.html',
        controller: 'MessageCtrl'
    }).otherwise({
        redirectTo: '/category'
    });
});