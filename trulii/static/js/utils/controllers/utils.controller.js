-/**
* Register controller
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.utils.controllers')
    .controller('SimpleModalMsgCtrl', SimpleModalMsgCtrl);

  SimpleModalMsgCtrl.$inject = ['$scope','$modal','$http','$routeParams'];
  /**
  * @namespace RegisterController
  */
  function SimpleModalMsgCtrl($scope,$modal,$http,$routeParams) {


  	var template_name = $routeParams.template_name;
  	var module_name   = $routeParams.module_name;


	var modalInstance = $modal.open({
	    templateUrl: 'static/partials/'+module_name+'/messages/'+template_name+'.html',
	    controller: 'ModalInstanceCtrl',
	});

  };


	angular
	.module('trulii.utils.controllers')
	.controller('ModalInstanceCtrl', function ($scope, $modalInstance) {


		$scope.ok = function () {
			$modalInstance.close();
		};

		$scope.cancel = function () {
		};
	});

  })();