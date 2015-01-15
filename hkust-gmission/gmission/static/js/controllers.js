/**
 * Created by chenzhao on 17/2/14.
 */

var gmissionControllers = angular.module('gmissionControllers', ['restangular', 'angularFileUpload']);


gmissionControllers.controller('NaviBarCtrl', function($http, $rootScope, $scope, Restangular){
    $scope.testing_users = [
        {email:'zchenah@ust.hk', password:'111111'},
        {email:'test1@xxx.com', password:'111111'},
        {email:'test2@xxx.com', password:'111111'},
        {email:'test3@xxx.com', password:'111111'},
        {email:'test4@xxx.com', password:'111111'},
        {email:'test5@xxx.com', password:'111111'}
    ]
    $scope.login = function(email, password){
        $scope.email=email;
        $scope.password=password;
        $http.post('../../user/login', {email:email, password:password}).success(function(user){
            console.log(user);
            localStorage.setItem('user', JSON.stringify(user));
            $rootScope.user = user;
            $scope.logined = true;
//            $route.reload();
        })
    }
    var saved_user = JSON.parse(localStorage.getItem('user'))
    if (!saved_user){
        $scope.logined = false;
        $scope.login('zchenah@ust.hk', '111111');
    }else{
        $rootScope.user = saved_user;
        $scope.email=saved_user.email;
        $scope.logined = true;
    }
});

gmissionControllers.controller('MessageCtrl', function ($rootScope, $scope, Restangular) {
    Restangular.all('message').getList({q:{filters:[{name:"receiver_id", op:'eq', val:$rootScope.user.id},
        {name:"status", op:'eq', val:"new"}
    ]}}).then(function (msg) {
        $scope.messages = msg;
    });
});

gmissionControllers.controller('AllCategoryCtrl', function ($scope, Restangular) {

    $scope.position = null;
    navigator.geolocation.getCurrentPosition(function(position) {
        $scope.$apply(function(){
        console.log('getCurrentPosition', position)
        $scope.position = position;
          var pos = new google.maps.LatLng(position.coords.latitude,
                                       position.coords.longitude);
            console.log(pos);

        });
    });

    Restangular.all('indoor-category').getList().then(function (cate) {
        $scope.categories = cate;
    });
});

gmissionControllers.controller('CategoryCtrl', function ($scope, Restangular, $routeParams) {



    Restangular.one('indoor-category', $routeParams.id).get().then(function (cate) {
        $scope.category = cate
        $scope.locations = cate.locations;
    });
});

gmissionControllers.controller('LocationCtrl', function ($scope, $rootScope, Restangular, $http, $route, $routeParams) {
    Restangular.one('indoor-location', $routeParams.id).get().then(function (location) {

        Restangular.all('indoor-request').getList().then(function(requests){
            $scope.all_requests = requests;
        })

        Restangular.all('indoor-task').getList().then(function(tasks){
            $scope.all_tasks = tasks;
        })
//        location.tasks.forEach(function(task){
//            location.requests.forEach(function(request){
//                if (request.task_id==task.id){
//                    request.task = task;
//                }
//            });
//        });
        $scope.location = location;
//        $rootScope.requests = location.requests;

        $scope.new_request = {valid:10, brief:'I am asking something -'+$rootScope.user.name, location_id:location.id, type:'text' ,credit:10, required_answer_count:3};
        $scope.submit = function () {
            var r = $scope.new_request;
            r.begin_time = new Date();
            r.end_time = new Date(r.begin_time.getTime() + r.valid*60000);
            r.requester_id = $rootScope.user.id;
            $http.post('../../shortcut/request_new_indoor_task', r).success(function(data){
                console.log(data);
                $route.reload();
            })
        }
    });
});

gmissionControllers.controller('RequestCtrl', function ($scope, $rootScope, Restangular, $upload, $route, $routeParams, $http) {
    Restangular.one('indoor-request', $routeParams.id).get().then(function (request) {
        Restangular.one('indoor-task', request.task_id).get().then(function (task) {
        request.task = task;
        $scope.request = request;

        $scope.option_id = '';
        $scope.submit = function () {
            var r = {location_id:request.location_id,
                worker_id:$rootScope.user.id,
                request_id:request.id
            };
            console.log(task.type);
            if (task.type==='image' || task.type==='video'){
                r.value = $scope.uploaded_filename;
            } else{
                r.option_id = $scope.option_id;
            }
            Restangular.all('indoor-answer').post(r).then(function(data){
                console.log(data);
                $route.reload();
            })
        };
        $scope.close = function(){
            Restangular.one('indoor-request', request.id).customPUT({status:'closed'}).then(function(data){
                console.log(data);
                $route.reload();
            });
        }

        var upload_url = '../../' + task.type + '/upload';  //image or video
        $scope.onFileSelect = function ($files) {
            $scope.upload = $upload.upload({
                url: upload_url,
                method: 'POST',
                headers: {'headerKey': 'headerValue'},
                file: $files[0]
            }).progress(function (evt) {
                console.log('upload percent: ' + parseInt(100.0 * evt.loaded / evt.total));
            }).success(function (data, status, headers, config) {
                console.log('uploaded', data);
                $scope.uploaded_filename = data.filename;
            });
        };

        });
    });
});

