/**
* Register controller
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use strict';



  angular
    .module('trulii.authentication.controllers') 
    .controller('RegisterController', RegisterController);

  RegisterController.$inject = ['$location', '$scope', 'Authentication','$modal'];

  /**
  * @namespace RegisterController
  */
  function RegisterController($location, $scope, Authentication,$modal) {
    var vm = this;

    vm.items = ['item1', 'item2', 'item3'];

    vm.register = register;
    console.log(vm.$templateUrl);
    console.log(vm.$templateUrl);
    var size='lg';
    vm.open = $modal.open({
      templateUrl: 'myModalContent.html',
      controller: 'ModalInstanceCtrl',
      size: size,
      resolve: {
        items: function () {
          return vm.items;
        },
        
      }
    });


    /**
    * @name register
    * @desc Register a new user
    * @memberOf thinkster.authentication.controllers.RegisterController
    */
    function register() {
      Authentication.register(vm.email, vm.password, vm.username);
    }
  }



    angular
    .module('trulii.authentication.controllers').controller('ModalInstanceCtrl', function ($scope, $modalInstance, items) {

    $scope.items = items;
    $scope.selected = {
      item: $scope.items[0]
    };

    $scope.ok = function () {
      $modalInstance.close($scope.selected.item);
    };

    $scope.cancel = function () {
      $modalInstance.dismiss('cancel');
    };
  });

})();