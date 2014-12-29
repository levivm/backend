-/**
* Register controller
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.authentication.controllers')
    .controller('EmailConfirmCtrl', EmailConfirmCtrl);

  EmailConfirmCtrl.$inject = ['$scope', 'Authentication','$modal','$http','$routeParams'];
  /**
  * @namespace RegisterController
  */
  function EmailConfirmCtrl($scope, Authentication,$modal,$http,$routeParams) {


    Authentication.confirm_email($routeParams.confirmation_key);

    var modalInstance = $modal.open({
      templateUrl: 'static/partials/email_confirm.html',
      controller: 'ModalInstanceCtrl',
      // size: size,
      // resolve: {
      //   items: function () {
      //     return $scope.items;
      //   }
      // }
    });

  };

 //  	angular
	// .module('trulii.authentication.controllers')
	// .controller('ModalInstanceCtrl', function ($scope, $modalInstance) {


	//   $scope.ok = function () {
	//     $modalInstance.close();
	//   };

	//   $scope.cancel = function () {
	//   };
	// });



  })();