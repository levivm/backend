/**
* LoginController
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use static';

  angular
    .module('trulii.authentication.controllers')
    .controller('ForgotPasswordCtrl', ForgotPasswordCtrl);

  ForgotPasswordCtrl.$inject = ['$location', '$scope', 'Authentication','$modal','$stateParams'];

  /**
  * @namespace ForgotPasswordCtrl
  */
  function ForgotPasswordCtrl($location, $scope, Authentication,$modal,$stateParams) {
    var vm = this;


    if ($stateParams.confirmation_key_done){

      var modalInstance = $modal.open({
        templateUrl: 'static/partials/authentication/password_reset_key_done.html',
        controller: 'ModalInstanceCtrl',
      });
    }

    $scope.user = {};

    $scope.errors = {};
    $scope.forgotPassword = forgotPassword;

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
    * @name login
    * @desc Log the user in
    * @memberOf thinkster.authentication.controllers.LoginController
    */
    function forgotPassword() {
      _clearErrors();

     // return  Authentication.login($scope.user.login, $scope.user.password)
     //          .error(_errored)
     //          .success(function(data){

     //            console.log("success");
     //            console.log(data);
     //          });
     console.log('auth');
     console.log(Authentication);
     return  Authentication.reset_password($scope.user.email)
              .error(passwordResetErrorFn)
              .success(passwordResetFn);
    }


    /**
     * @name passwordResetFn
     * @desc Set the authenticated account and redirect to index
     */
    function passwordResetFn(data, status, headers, config) {

      console.log('data to store');
      console.log(data);
      console.log($scope.user);

      var modalInstance = $modal.open({
        templateUrl: 'static/partials/authentication/password_reset_done.html',
        controller: 'ModalInstanceCtrl',
        // size: size,
        // resolve: {
        //   items: function () {
        //     return $scope.items;
        //   }
        // }
      });
      //Authentication.setAuthenticatedAccount($scope.user);

      //window.location = '/';
    }

    /**
     * @name passwordResetErrorFn
     * @desc Log "Epic failure!" to the console
     */
    function passwordResetErrorFn(data, status, headers, config) {
      _errored(data);
    }




  }
})();