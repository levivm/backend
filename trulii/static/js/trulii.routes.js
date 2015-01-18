(function () {
  'use strict';

  angular
    .module('trulii.routes')
    .config(config);

  config.$inject = ['$urlRouterProvider','$stateProvider'];

  /**
  * @name config
  * @desc Define valid application routes
  */
  function config($urlRouterProvider,$stateProvider) {
   

    // when('/register', {
    //   controller: 'RegisterController', 
    //   controllerAs: 'vm',
    //   templateUrl: 'static/partials/authentication/register.html'
    // })
    // .when('/confirm-email/:confirmation_key', {
    //   controller: 'EmailConfirmCtrl', 
    //   //controllerAs: 'vm',
    //   //templateUrl: 'static/partials/email_confirm.html' url(r"
    //   templateUrl: 'modalContainer' 
    // })
    // .when('/password/reset/', {
    //   //ontroller: 'ForgotPasswordCtrl', 
    //   //controllerAs: 'vm',
    //   //templateUrl: 'static/partials/email_confirm.html' url(r"
    //   templateUrl: 'modalContainer' 
    // })
    // .when('/messages/:module_name/:template_name/', {
    //   controller: 'SimpleModalMsgCtrl', 
    //   //controllerAs: 'vm',
    //   //templateUrl: 'static/partials/email_confirm.html' url(r"
    //   templateUrl: 'modalContainer' 
    // })
    // .when('/organizer/dashboard/', {
    //   controller: 'OrganizerDashboardCtrl', 
    //   //controllerAs: 'vm',
    //   templateUrl: 'static/partials/organizers/dashboard.html',
    //   //templateUrl: 'modalContainer' 
    // })
    // .when('/activities/new/', {
    //   controller: 'ActivityCreationCtrl', 
    //   //controllerAs: 'vm',
    //   templateUrl: 'static/partials/activities/new_activitie.html',
    //   //templateUrl: 'modalContainer' 
    // })
    // .when('/activities/edit/:activity_id/', {
    //   controller: 'ActivityCreationCtrl', 
    //   //controllerAs: 'vm',
    //   templateUrl: 'static/partials/activities/new_activitie.html',
    //   //templateUrl: 'modalContainer' 
    // })
    // .otherwise({redirectTo: '/'});



    $stateProvider
    .state("register", {
      url:'register',
      controller: 'RegisterController', 
      //controllerAs: 'vm',
      templateUrl: 'static/partials/authentication/register.html'
    })
    .state('confirm_email', {
      url:'/confirm-email/:confirmation_key',
      controller: 'EmailConfirmCtrl', 
      //controllerAs: 'vm',
      //templateUrl: 'static/partials/email_confirm.html' url(r"
      templateUrl: 'modalContainer' 
    })
    .state('password_reset', {
      url:'/password/reset/',
      //ontroller: 'ForgotPasswordCtrl', 
      //controllerAs: 'vm',
      //templateUrl: 'static/partials/email_confirm.html' url(r"
      templateUrl: 'modalContainer' 
    })
    .state('general-message', {
      url:'/messages/:module_name/:template_name/',
      controller: 'SimpleModalMsgCtrl', 
      //controllerAs: 'vm',
      //templateUrl: 'static/partials/email_confirm.html' url(r"
      templateUrl: 'modalContainer' 
      //templateUrl: 'static/partials/authentication/register.html'
    })
    .state('organizer_dashboard/', {
      url:'/organizer/dashboard/',
      controller: 'OrganizerDashboardCtrl', 
      //controllerAs: 'vm',
      templateUrl: 'static/partials/organizers/dashboard.html',
      //templateUrl: 'modalContainer' 
    })
    .state('activties-new', {
      url:'/activities/new/',
      controller: 'ActivityCreationCtrl', 
      //controllerAs: 'vm',
      templateUrl: 'static/partials/activities/new_activitie.html',
      //templateUrl: 'modalContainer' 
    })
    .state('activties-edit', {
      url:'/activities/edit/:activity_id/',
      controller: 'ActivityCreationCtrl', 
      //controllerAs: 'vm',
      templateUrl: 'static/partials/activities/new_activitie.html',
      //templateUrl: 'modalContainer' 
    });

    //$urlRouterProvider.otherwise('/');

  }
})();

