var dashboardApp = angular.module('dashboardApp', [
    'ngRoute',
    'dashboardControllers'
]);

dashboardApp.factory('statsService', ['$interval', '$http', function($interval, $http) {
    var service = {};
    service.master = null;
    service.stats = {};
    service.frameworks = [];
    service.tasks = {};
    var updateStats = function() {
        $http.get('/api/nodes/stats').success(function(data) {
            service.master = data.master;
            service.stats = data.nodes;
            service.frameworks = data.frameworks;
            service.tasks = data.tasks;
        });
    }
    service.getFrameworkTasks = function(frameworkId) {
        var result = [];
        var framework = service.frameworks[frameworkId];
        if (!framework.tasks) { return []; }
        for (t in framework.tasks) {
            var t = framework.tasks[t];
            if (!t) { continue; }
            var node = service.stats[service.tasks[t]];
            if (node && node.tasks[t]) {
            console.log(node.tasks[t]);
                result.push(node.tasks[t]);
            }
        }
        return result;
    };

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
                when('/frameworks/:frameworkId', {
                    templateUrl: 'static/partials/framework.html',
                    controller: 'frameworksController',
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
dashboard.controller('frameworksController', ['$scope', 'statsService', 'pageService', '$routeParams', function($scope, statsService, pageService, $routeParams) {
    $scope.statsService = statsService;
    $scope.frameworkId = $routeParams.frameworkId;
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
