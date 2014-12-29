  	angular
	.module('trulii.utils.controllers')
	.controller('ModalInstanceCtrl', function ($scope, $modalInstance) {


	  $scope.ok = function () {
	    $modalInstance.close();
	  };

	  $scope.cancel = function () {
	  };
	});