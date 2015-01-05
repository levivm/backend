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
    .when('/confirm-email/:confirmation_key', {
      controller: 'EmailConfirmCtrl', 
      //controllerAs: 'vm',
      //templateUrl: 'static/partials/email_confirm.html' url(r"^
      templateUrl: 'modalContainer' 
    })
    .when('/password/reset/', {
      //ontroller: 'ForgotPasswordCtrl', 
      //controllerAs: 'vm',
      //templateUrl: 'static/partials/email_confirm.html' url(r"^
      templateUrl: 'modalContainer' 
    });;
    //.otherwise({redirectTo: '/'});

  }
})();

