var dashboard = angular.module('mesos-dashboard', [])


dashboard.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.useXDomain = true;
    delete $httpProvider.defaults.headers.common['X-Requested-With'];
}])


dashboard.controller('dashboardController', ['$scope', '$http', function($scope, $http) {

  $http.get('/api/nodes/stats').success(function(data) {
    $scope.master = data.master;
    $scope.stats = data.nodes;
  });
}]);
