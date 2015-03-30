/**
* LoginController
* @namespace thinkster.authentication.controllers
*/
(function () {
  'use static';

  angular
    .module('trulii.authentication.controllers')
    .controller('ForgotPasswordCtrl', ForgotPasswordCtrl);

  ForgotPasswordCtrl.$inject = ['$scope','$location','$modal','$state','$stateParams','Authentication'];

  /**
  * @namespace ForgotPasswordCtrl
  */
  function ForgotPasswordCtrl($scope, $location,$modal,$state,$stateParams,Authentication) {
    var vm = this;

    console.log("state params",$stateParams);
    console.log("state params",$stateParams);
    console.log("state params",$stateParams);

    if ($stateParams.reset_key){

      var modalInstance = $modal.open({
        templateUrl: 'static/partials/authentication/reset_password.html',
        controller: 'ResetPasswordCtrl',
        controllerAs:'vm'
      });

      modalInstance.result.then(function(){

      $state.go('general-message',{'module_name':'authentication',
                                   'template_name':'change_password_success',
                                   'redirect_state':'home'});

      });

    }
    else if ($stateParams.confirmation_key_done){

      var modalInstance = $modal.open({
        templateUrl: 'static/partials/authentication/password_reset_key_done.html',
        controller: 'ModalInstanceCtrl',
      });
    }
    // else{

    //   var modalInstance = $modal.open({
    //     templateUrl: 'static/partials/authentication/reset_password.html',
    //     controller: 'ResetPasswordCtrl',
    //     controllerAs:'vm'
    //   });

    // }

    vm.user = {};

    vm.errors = {};
    vm.forgotPassword = forgotPassword;

    vm.clearErrors = _clearErrors;

    function _clearErrors(){
      vm.errors = null;
      vm.errors = {};
    }



    function _addError(field, message) {

      vm.errors[field] = message;
      vm.forgot_password_form[field].$setValidity(message, false);


    };


        // vm.form[field].$setValidity('server', false)
        // # keep the error messages from the server
        // vm.errors[field] = errors.join(', ')


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

     // return  Authentication.login(vm.user.login, vm.user.password)
     //          .error(_errored)
     //          .success(function(data){

     //            console.log("success");
     //            console.log(data);
     //          });
     console.log('auth');
     return  Authentication.forgot_password(vm.user.email)
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
      console.log(vm.user);

      var modalInstance = $modal.open({
        templateUrl: 'static/partials/authentication/password_reset_done.html',
        controller: 'ModalInstanceCtrl',
        // size: size,
        // resolve: {
        //   items: function () {
        //     return vm.items;
        //   }
        // }
      });
      //Authentication.setAuthenticatedAccount(vm.user);

      //window.location = '/';
    }

    /**
     * @name passwordResetErrorFn
     * @desc Log "Epic failure!" to the console
     */
    function passwordResetErrorFn(data) {
      console.log("errroor",data);
      _errored(data);
    }




  }
})();