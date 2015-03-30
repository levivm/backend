/**
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
    


  RegisterController.$inject = ['$scope','$q','Authentication','$modal','$http'];


  function RegisterController($scope, $q, Authentication,$modal,$http) {
    var vm = this;

    

    vm.set_usertype = function function_name(user_type) {
      vm.user_type = user_type;
    }

    vm.user   = {};
    vm.errors = {};

    vm.register = register;



    function _clearErrors(){
      vm.errors = null;
      vm.errors = {};
    }



    function _addError(field, message) {

      vm.errors[field] = message;

    };


    function _errored(data) {
      if (data['form_errors']) {

        angular.forEach(data['form_errors'], function(errors, field) {

          _addError(field, errors[0]);

        });

      }
    }


    function register() {
      _clearErrors();
      vm.user.user_type = vm.user_type;
      return Authentication.register(vm.user.email, vm.user.password1,
                                     vm.user.first_name, vm.user.last_name,
                                     vm.user.user_type)
            .then(function(response){

              console.log("success");
              console.log(response);
              //HERE SHOULD HSHOW A POP UP

            },_registerError);

    }

    function _registerError(response){
      _errored(response.data);
      return $q.reject(response);

    }
  }


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