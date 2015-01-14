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
      templateUrl: 'static/partials/authentication/register.html'
    })
    .when('/confirm-email/:confirmation_key', {
      controller: 'EmailConfirmCtrl', 
      //controllerAs: 'vm',
      //templateUrl: 'static/partials/email_confirm.html' url(r"
      templateUrl: 'modalContainer' 
    })
    .when('/password/reset/', {
      //ontroller: 'ForgotPasswordCtrl', 
      //controllerAs: 'vm',
      //templateUrl: 'static/partials/email_confirm.html' url(r"
      templateUrl: 'modalContainer' 
    })
    .when('/messages/:module_name/:template_name/', {
      controller: 'SimpleModalMsgCtrl', 
      //controllerAs: 'vm',
      //templateUrl: 'static/partials/email_confirm.html' url(r"
      templateUrl: 'modalContainer' 
    })
    .when('/organizer/dashboard/', {
      controller: 'OrganizerDashboardCtrl', 
      //controllerAs: 'vm',
      templateUrl: 'static/partials/organizers/dashboard.html',
      //templateUrl: 'modalContainer' 
    })
    .when('/activities/new/', {
      controller: 'ActivityCreationCtrl', 
      //controllerAs: 'vm',
      templateUrl: 'static/partials/activities/new_activitie.html',
      //templateUrl: 'modalContainer' 
    });
    //.otherwise({redirectTo: '/'});

  }
})();

