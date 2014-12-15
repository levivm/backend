/**
* Register controller
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use strict';



  angular
    .module('trulii.authentication.controllers')
    .controller('RegisterController', RegisterController);
  //   .directive('formModal', ['$http','$compile',function() {
  //   return {
  //     scope: {
  //       formObject: '=',
  //       formErrors: '=',
  //       title: '@',
  //       template: '@',
  //       okButtonText: '@',
  //       formSubmit: '&'
  //     },
  //     compile: function(element, cAtts){
  //       var template,
  //         $element,
  //         loader;

  //       loader = $http.get('partials/form_modal.html')
  //         .success(function(data) {
  //           template = data;
  //         });

  //       //return the Link function
  //       return function(scope, element, lAtts) {
  //         loader.then(function() {
  //           //compile templates/form_modal.html and wrap it in a jQuery object
  //           $element = $( $compile(template)(scope) );
  //         });

  //         //called by form_modal.html cancel button
  //         scope.close = function() {
  //           $element.modal('hide');
  //         };

  //         //called by form_modal.html form ng-submit
  //         scope.submit = function() {
  //           var result = scope.formSubmit();

  //           if (Object.isObject(result)) {
  //             result.success(function() {
  //               $element.modal('hide');
  //             });
  //           } else if (result === false) {
  //             //noop
  //           } else {
  //             $element.modal('hide');
  //           }
  //         };

  //         element.on('click', function(e) {
  //           e.preventDefault();
  //           $element.modal('show');
  //         });
  //       };
  //     }
  //   }
  // }]);

  RegisterController.$inject = ['$location', '$scope', 'Authentication','$modal'];

  /**
  * @namespace RegisterController
  */
  function RegisterController($location, $scope, Authentication,$modal) {
    var vm = this;

    //vm.items = ['item1', 'item2', 'item3'];

    vm.user = {'username':'','password':''};
    vm.register = register;
    // console.log(vm.$templateUrl);
    // console.log(vm.$templateUrl);
    // var size='lg';
    // vm.open = $modal.open({
    //   templateUrl: 'myModalContent.html',
    //   controller: 'ModalInstanceCtrl',
    //   size: size,
    //   resolve: {
    //     items: function () {
    //       return vm.items;
    //     },
        
    //   }
    // });


    /**
    * @name register
    * @desc Register a new user
    * @memberOf thinkster.authentication.controllers.RegisterController
    */
    function register() {
      Authentication.register(vm.email, vm.password, vm.username);
    }
  }



  //   angular
  //   .module('trulii.authentication.controllers').controller('ModalInstanceCtrl', function ($scope, $modalInstance, items) {

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