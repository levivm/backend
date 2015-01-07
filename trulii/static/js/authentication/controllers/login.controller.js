/**
* LoginController
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use static';

  angular
    .module('trulii.authentication.controllers')
    .controller('LoginController', LoginController);

  LoginController.$inject = ['$location', '$scope', 'Authentication'];

  /**
  * @namespace LoginController
  */
  function LoginController($location, $scope, Authentication) {
    var vm = this;

    $scope.user = {};


    $scope.errors = {};
    $scope.login = login;
    $scope.is_new = true;

    activate();


    $scope.clearErrors = _clearErrors;

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
    * @name activate
    * @desc Actions to be performed when this controller is instantiated
    * @memberOf thinkster.authentication.controllers.LoginController
    */
    function activate() {
      // If the user is authenticated, they should not be here.
      if (Authentication.isAuthenticated()) {
        $location.url('/');
      }
    }

    /**
    * @name login
    * @desc Log the user in
    * @memberOf thinkster.authentication.controllers.LoginController
    */
    function login() {
      _clearErrors();

     // return  Authentication.login($scope.user.login, $scope.user.password)
     //          .error(_errored)
     //          .success(function(data){

     //            console.log("success");
     //            console.log(data);
     //          });

     return  Authentication.login($scope.user.login, $scope.user.password)
              .error(loginErrorFn)
              .success(loginSuccessFn);
    }


    /**
     * @name loginSuccessFn
     * @desc Set the authenticated account and redirect to index
     */
    function loginSuccessFn(data, status, headers, config) {
      console.log('data to store');
      console.log($scope.user);
      Authentication.setAuthenticatedAccount($scope.user);

      //window.location = '/';
    }

    /**
     * @name loginErrorFn
     * @desc Log "Epic failure!" to the console
     */
    function loginErrorFn(data, status, headers, config) {
      _errored(data);

    }




  }
})();