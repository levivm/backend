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
   



    $stateProvider
    .state("home",{
      url:"/",
      controller:'HomeController',
      resolve:{


        cities:getAvailbleCities
      },
      templateUrl: 'static/partials/landing/landing.html'
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
    .state('confirm-email', {
      url:'/confirm-email/:confirmation_key',
      controller: 'EmailConfirmCtrl', 
      //controllerAs: 'vm',
      //templateUrl: 'static/partials/email_confirm.html' url(r"
      templateUrl: 'modalContainer' 
    })
    .state('password-reset', {
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
    .state('organizer-dashboard', {
      abstract:true,
      url:'/organizer/dashboard/',
      controller: 'OrganizerDashboardCtrl', 
      controllerAs: 'vm',
      templateUrl: 'static/partials/organizers/dashboard.html',
      data: {

        requiredAuthentication : true
      },
      //templateUrl: 'modalContainer' 
    })
    .state('organizer-dashboard.profile', {
      url:'profile',
      controller: 'OrganizerProfileCtrl', 
      controllerAs: 'vm',
      templateUrl: 'static/partials/organizers/dashboard_profile.html',
      //templateUrl: 'modalContainer' 
    })
    .state('organizer-dashboard.account', {
      url:'account',
      controller: 'OrganizerAccountCtrl', 
      controllerAs: 'vm',
      templateUrl: 'static/partials/organizers/dashboard_account.html',
      //templateUrl: 'modalContainer' 
    })
    .state('organizer-dashboard.activities', {
      url:'',
      controller: 'OrganizerAccountCtrl', 
      //controllerAs: 'vm',
      templateUrl: 'static/partials/organizers/dashboard_activities.html',
      //templateUrl: 'modalContainer' 
    })
    .state('activties-new', {
      abstract:true,
      url:'/activities/new/',
      //controller: 'ActivityGeneralController',
      data: {

        requiredAuthentication : true
      },
      resolve: {

        activity: getActivity

      },
      //controllerAs: 'vm',
      templateUrl: 'static/partials/activities/create.html',
      //templateUrl: 'modalContainer' 
    })
    .state('activties-new.general', {
      url:'',
      controller: 'ActivityGeneralController',
      controllerAs: 'vm',
      templateUrl: 'static/partials/activities/dashboard_general.html',
      //templateUrl: 'modalContainer' 
    })
    .state('activities-edit', {
      abstract:true,
      url:'/activities/edit/{activity_id:int}/', 
      controller: 'ActivityDashboardCtrl', 
      data: {

        requiredAuthentication : true
      },
      resolve: {

        activity: getActivity,

      },
      controllerAs: 'pc',
      templateUrl: 'static/partials/activities/edit.html',

      //templateUrl: 'modalContainer' 
    })
    .state('activities-edit.general', {
      url:'', 
      controller: 'ActivityGeneralController', 
      controllerAs: 'vm',
      templateUrl: 'static/partials/activities/dashboard_general.html',
      //templateUrl: 'modalContainer' 
    })
    .state('activities-edit.detail', {
      url:'detail', 
      controller: 'ActivityDBDetailController', 
      // resolve:{
      //   activity : getParentActivity

      // },
      controllerAs: 'vm',
      templateUrl: 'static/partials/activities/dashboard_detail.html',
      //templateUrl: 'modalContainer' 
    })
    .state('activities-edit.calendars', {
      url:'calendars', 
      controller: 'ActivityCalendarsController', 
      controllerAs: 'vm',
      templateUrl: 'static/partials/activities/dashboard_calendars.html',
      resolve:{

        calendars:getCalendars
      }
      //templateUrl: 'modalContainer' 
    })
    .state('activities-edit.calendars.detail' ,{
      url:'?id',
      controller: 'ActivityCalendarController',
      controllerAs: 'vm',
      templateUrl: 'static/partials/activities/dashboard_calendar_detail.html',
      resolve: {

        calendar: getCalendar
      }
    })
    .state('activities-edit.location', {
      url:'location', 
      controller: 'ActivityDBLocationController', 
      resolve:{


        cities:getAvailbleCities
      },
      controllerAs: 'vm',
      templateUrl: 'static/partials/activities/dashboard_location.html',
    })
    .state('activities-edit.gallery', {
      url:'gallery', 
      controller: 'ActivityDBGalleryController', 
      controllerAs: 'vm',
      templateUrl: 'static/partials/activities/dashboard_gallery.html',
    })
    .state('activities-edit.return-policy', {
      url:'return-policy', 
      controller: 'ActivityDBReturnPDashboard', 
      controllerAs: 'vm',
      templateUrl: 'static/partials/activities/dashboard_return_policy.html',
    });
    

    

    //$urlRouterProvider.otherwise('/');

  }




  /****** RESOLVER FUNCTIONS *******/


  getAvailbleCities.$inject = ['$stateParams','$q','LocationManager'];

  function getAvailbleCities($stateParams,$q,LocationManager){

    return LocationManager.getAvailableCities()
  }


  getCalendars.$inject = ['CalendarsManager','activity'];

  function getCalendars( CalendarsManager, activity){
    var calendars = CalendarsManager.loadCalendars(activity.id);
    return calendars;
  }

  getCalendar.$inject = ['$stateParams','CalendarsManager','activity'];

  function getCalendar($stateParams, CalendarsManager, activity){

    var calendar_id = $stateParams.id;
    
    //console.log("Calendar id",CalendarsManager.getCalendar(calendar_id));
    console.log("Calendar id",$stateParams);
    //var calendar = 
    return CalendarsManager.getCalendar(calendar_id);
  }



  getActivity.$inject = ['$stateParams','$q','Activity'];
  
  function getActivity($stateParams,$q,Activity){

    var activity = new Activity();
    if (!$stateParams.activity_id){
      var deferred = $q.defer();
      deferred.resolve(activity);
      return deferred.promise;
    }

    return activity.load($stateParams.activity_id)
  }



  /****** RUN METHOD*******/
  run.$inject = ['$rootScope','$state','Authentication'];

  function run($rootScope,$state,Authentication){

    $rootScope.$on('$stateChangeStart',function(e,toState){



      if ( !(toState.data) ) return;
      if ( !(toState.data.requiredAuthentication) ) return;

      var _requiredAuthentication = toState.data.requiredAuthentication;

      if (_requiredAuthentication && !Authentication.isAuthenticated()){

        e.preventDefault();
        $state.go('home',{'notify':false});
      }
      return;


    });
  };
})();

