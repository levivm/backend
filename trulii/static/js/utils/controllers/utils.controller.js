-/**
* Register controller
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.utils.controllers')
    .controller('SimpleModalMsgCtrl', SimpleModalMsgCtrl);

  SimpleModalMsgCtrl.$inject = ['$scope','$modal','$http','$stateParams','$state'];
  /**
  * @namespace RegisterController
  */
  function SimpleModalMsgCtrl($scope,$modal,$http,$stateParams,$state) {


  	var template_name  = $stateParams.template_name;
  	var module_name    = $stateParams.module_name;
  	


	var modalInstance = $modal.open({
	    templateUrl: 'static/partials/'+module_name+'/messages/'+template_name+'.html',
	    controller: 'ModalInstanceCtrl',
	});

	modalInstance.result.then(function(){

		var redirect_state = $stateParams.redirect_state;
		if(redirect_state)
			$state.go(redirect_state);
	})

  };


	angular
	.module('trulii.utils.controllers')
	.controller('ModalInstanceCtrl', function ($scope, $modalInstance) {


		$scope.ok = function () {
			$modalInstance.close();
		};

		$scope.cancel = function () {
			$modalInstance.dismiss();
		};
	});


  angular
    .module('trulii.utils.controllers')
    .controller('DialogModalCtrl', DialogModalCtrl);

  DialogModalCtrl.$inject = ['$scope','$modal','$http','$stateParams','$state'];
  /**
  * @namespace RegisterController
  */
  function DialogModalCtrl($scope,$modal,$http,$stateParams,$state) {
  	


	var modalInstance = $modal.open({
	    templateUrl:'static/partials/utils/base_dialog_modal.html',
	    controller: 'ModalInstanceCtrl',
	});

  };

  })();