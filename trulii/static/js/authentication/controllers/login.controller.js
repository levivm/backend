/**
* LoginController
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use static';

  angular
    .module('trulii.authentication.controllers')
    .controller('LoginController', LoginController);

  LoginController.$inject = ['$scope', '$location', '$state','$q','Authentication'];

  /**
  * @namespace LoginController
  */
  function LoginController($scope, $location, $state, $q, Authentication) {
    var vm = this;

    vm.user = {};


    vm.errors = {};
    vm.login = login;
    vm.is_new = true;



    vm.clearErrors = _clearErrors;

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



    /**
    * @name login
    * @desc Log the user in
    * @memberOf thinkster.authentication.controllers.LoginController
    */
    function login() {
      _clearErrors();

     return  Authentication.login(vm.user.login, vm.user.password)
              .then(_loginSuccess,_loginError)
              //.error(loginErrorFn)
              //.success(loginSuccessFn);
    }


    /**
     * @name loginSuccessFn
     * @desc Set the authenticated account and redirect to index
     */
    function _loginSuccess(response) {

      //Authentication.updateAuthenticatedAccount();
      $state.reload();
      //window.location = '/';
    }

    /**
     * @name loginErrorFn
     * @desc Log "Epic failure!" to the console
     */
    function _loginError(response) {
      _errored(response.data);
      return $q.reject(response);

    }




  }
})();