/**
* Register controller
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use strict';



  angular
    .module('trulii.authentication.controllers') 
    .controller('RegisterController', RegisterController);

  RegisterController.$inject = ['$location', '$scope', 'Authentication'];

  /**
  * @namespace RegisterController
  */
  function RegisterController($location, $scope, Authentication) {
    var vm = this;


    vm.register = register;

    /**
    * @name register
    * @desc Register a new user
    * @memberOf thinkster.authentication.controllers.RegisterController
    */
    function register() {
      Authentication.register(vm.email, vm.password, vm.username);
    }
  }



  // angular.module('ui.bootstrap.demo').controller('ModalInstanceCtrl', function ($scope, $modalInstance, items) {

  //   $scope.items = items;
  //   $scope.selected = {
  //     item: $scope.items[0]
  //   };

  //   $scope.ok = function () {
  //     $modalInstance.close($scope.selected.item);
  //   };

  //   $scope.cancel = function () {
  //     $modalInstance.dismiss('cancel');
  //   };
  // });

})();