(function () {
  'use strict';



	angular
	.module('trulii', [
	  'ui.bootstrap',
	  'trulii.config',
	  'trulii.routes',
	  'trulii.authentication',
	  'trulii.organizers',
    'trulii.utils'

	]);


	angular
  	.module('trulii.config',[]);

	angular
	.module('trulii.routes',['ngRoute']);




	angular
	  .module('trulii')
	  .run(run);

	run.$inject = ['$rootScope','$http','$cookies','Authentication'];








	/**
	* @name run
	* @desc Update xsrf $http headers to align with Django's defaults
	*/
	function run($rootScope,$http,$cookies,Authentication) {


		//$http.defaults.headers.post['X-CSRFToken'] = $cookies['csrftoken'];

	    $rootScope.$watch(function() { return $cookies.authenticatedAccount	;}, function(newValue) {
	    	if ($cookies.authenticatedAccount == null)
	    		console.log('hacer loggout');
	        console.log('Cookie string: ' + $cookies.authenticatedAccount)
	    });

	  $http.defaults.xsrfHeaderName = 'X-CSRFToken';
	  $http.defaults.xsrfCookieName = 'csrftoken';
	}

})();



