-/**
* Register controller
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use strict';



  angular
    .module('trulii.authentication.controllers')
    .controller('RegisterController', RegisterController);

  angular
    .module('trulii.authentication.controllers')
    .directive('serverError',serverError);

  angular
    .module('trulii.authentication.controllers')
    


  



  RegisterController.$inject = ['$location', '$scope', 'Authentication','$modal','$http'];

  /**
  * @namespace RegisterController
  */
  function RegisterController($location, $scope, Authentication,$modal,$http) {
    var vm = this;

    
    //vm.user = {};
    console.log('calling the controller');

    $scope.set_usertype = function function_name(user_type) {
      $scope.user_type = user_type;
    }

    $scope.user = {};
    $scope.errors = {};
    $scope.user.user_type = $scope.user_type;
    
    $scope.$watch("user_type", function(){
      $scope.user.user_type = $scope.user_type;
    });

    $scope.register = register;
    //vm.register = register;



    function _clearErrors(){
      $scope.errors = null;
      $scope.errors = {};
    }



    function _addError(field, message) {

      $scope.errors[field] = message;

    };


        // $scope.form[field].$setValidity('server', false)
        // # keep the error messages from the server
        // $scope.errors[field] = errors.join(', ')


    function _errored(response) {

      if (response['form_errors']) {

        angular.forEach(response['form_errors'], function(errors, field) {

          _addError(field, errors[0]);

        });

      }
    }

    /**
    * @name register
    * @desc Register a new user
    * @memberOf thinkster.authentication.controllers.RegisterController
    */
    function register() {
      _clearErrors();
      return Authentication.register($scope.user.email, $scope.user.password1,
                                     $scope.user.first_name, $scope.user.last_name,
                                     $scope.user.user_type)
            .error(_errored)
            .success(function(data){

              console.log("success");
              console.log(data);
            });
    }
  }






  //serverError.$inject = [''];

  function serverError(){
    return {
      restrict: 'A',
      require: '?ngModel',
      link: function (scope, element, attrs, ctrl) {

        element.on('change',function(event){

          scope.$apply(function () {
            console.log("aqui");
            ctrl.$setValidity('server', true);

          });

        });
      }
    }

  };

})();