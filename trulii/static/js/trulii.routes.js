(function () {
  'use strict';

  angular
    .module('trulii.routes')
    .config(config)
    .run(run);

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
    .state("home",{
      url:"/"
      //templateUrl: 'static/partials/authentication/register.html'
    })
    .state("register", {
      url:'register',
      controller: 'RegisterController', 
      //controllerAs: 'vm',
      templateUrl: 'static/partials/authentication/register.html'
    })
    .state("logout",{
      url:'/logout/',
      controller: 'LogOutController'
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
      data: {

        requiredAuthentication : true
      },
      //controllerAs: 'vm',
      templateUrl: 'static/partials/activities/new_activitie.html',
      //templateUrl: 'modalContainer' 
    })
    .state('activities-edit', {
      url:'/activities/edit/{activity_id:int}/', 
      controller: 'ActivityCreationCtrl', 
      //controllerAs: 'vm',
      templateUrl: 'static/partials/activities/new_activitie.html',
      //templateUrl: 'modalContainer' 
    });

    //$urlRouterProvider.otherwise('/');

  }

  run.$inject = ['$rootScope','$state','Authentication'];

  function run($rootScope,$state,Authentication){

    $rootScope.$on('$stateChangeStart',function(e,toState){

      if ( !(toState.data) ) return;
      if ( !(toState.data.requiredAuthentication) ) return;

      var _requiredAuthentication = toState.data.requiredAuthentication;

      console.log(_requiredAuthentication);
      console.log("is",Authentication.isAuthenticated());
      if (_requiredAuthentication && !Authentication.isAuthenticated()){

        e.preventDefault();
        $state.go('home',{'notify':false});
      }
      return;


    });
  };
})();

