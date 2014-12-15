(function () {
  'use strict';



	angular
	.module('trulii', [
	  'ui.bootstrap',
	  'trulii.config',
	  'trulii.routes',
	  'trulii.authentication',

	]);


	angular
  	.module('trulii.config',[]);

	angular
	.module('trulii.routes',['ngRoute']);


	angular
	  .module('trulii')
	  .run(run);

	run.$inject = ['$http','$cookies'];

	/**
	* @name run
	* @desc Update xsrf $http headers to align with Django's defaults
	*/
	function run($http,$cookies) {

		//$http.defaults.headers.post['X-CSRFToken'] = $cookies['csrftoken'];
	  $http.defaults.xsrfHeaderName = 'X-CSRFToken';
	  $http.defaults.xsrfCookieName = 'csrftoken';
	}

})();



