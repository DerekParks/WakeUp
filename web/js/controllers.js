var app = angular.module("wakeup", ["ngRoute", "ngMessages", "ngAnimate", "ui.bootstrap"]);

app.config(function($routeProvider) {
  $routeProvider.when('/MainCtrl', {
    controller: 'MainCtrl',
    templateUrl: 'main.html'
  })
    .otherwise({
      redirectTo: '/MainCtrl'
    });
})
.controller("MainCtrl", function($scope, $http, $log) {
    $scope.wakeup = function(machineName) {
      $log.debug("Waking up " + machineName);

        $http({
            method: 'GET',
            url: 'http://127.0.0.1:5000/wakeup/'+machineName
        }).then(function successCallback(response) {
            $log.debug("Sucess waking up " + machineName);
        }, function errorCallback(response) {
            $log.error("HTTP error waking up machine: " + response.status + " " + response.statusText);
        });        
    };
    
    $http({
        method: 'GET',
        url: 'http://127.0.0.1:5000/machines'
    }).then(function successCallback(response) {
        $scope.machines = response.data;
    }, function errorCallback(response) {
        $log.error("HTTP error getting machines:" + response.status + " " + response.statusText);
    });
});