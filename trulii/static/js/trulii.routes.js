(function () {
  'use strict';

  angular
    .module('trulii.routes')
    .config(config);

  config.$inject = ['$routeProvider'];

  /**
  * @name config
  * @desc Define valid application routes
  */
  function config($routeProvider) {
    $routeProvider.

    when('/register', {
      controller: 'RegisterController', 
      controllerAs: 'vm',
      templateUrl: 'static/partials/register.html'
    })
    .otherwise({redirectTo: '/'});

  }
})();

