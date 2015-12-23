var dashboardApp = angular.module('dashboardApp', [
    'ngRoute',
    'dashboardControllers'
]);

dashboardApp.factory('statsService', ['$interval', '$http', function($interval, $http) {
    var service = {};
    service.master = null;
    service.stats = {};
    service.frameworks = [];
    updateStats = function() {
        $http.get('/api/nodes/stats').success(function(data) {
            service.master = data.master;
            service.stats = data.nodes;
            service.frameworks = data.frameworks;
        });
    }
    updateStats();
    $interval(updateStats, 3000);
    return service;
}]);
dashboardApp.factory('pageService', [function() {
    var current = {'page': 'overview'}
    return current;
}]);

dashboardApp.config(['$routeProvider',
        function($routeProvider) {
            $routeProvider.
                when('/overview', {
                    templateUrl: 'static/partials/overview.html',
                    controller: 'overviewController'
                }).
                when('/frameworks', {
                    templateUrl: 'static/partials/frameworks.html',
                    controller: 'frameworksController'
                }).
                when('/nodes', {
                    templateUrl: 'static/partials/nodes.html',
                    controller: 'nodeController'
                }).
                when('/nodes/:nodeId', {
                    templateUrl: 'static/partials/node.html',
                    controller: 'nodeController'
                }).
                otherwise({
                    redirectTo: '/overview'
                });
        }]);

var dashboard = angular.module('dashboardControllers', [])


dashboard.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.useXDomain = true;
    delete $httpProvider.defaults.headers.common['X-Requested-With'];
}])


dashboard.controller('overviewController', ['$scope', 'statsService', 'pageService', function($scope, statsService, pageService) {
    $scope.statsService = statsService;
    pageService.page = 'overview';
}]);
dashboard.controller('frameworksController', ['$scope', 'statsService', 'pageService', function($scope, statsService, pageService) {
    $scope.statsService = statsService;
    pageService.page = 'frameworks';
}]);
dashboard.controller('nodeController', ['$scope', 'statsService', '$routeParams', 'pageService',
function($scope, statsService, $routeParams, pageService) {
    $scope.nodeId = $routeParams.nodeId;
    $scope.statsService = statsService;
    pageService.page = 'nodes';
}]);
dashboard.controller('navController', ['$scope', 'pageService', function($scope, pageService) {
    $scope.pageService = pageService;
}]);
