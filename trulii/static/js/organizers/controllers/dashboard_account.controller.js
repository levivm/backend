/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.organizers.controllers')
    .controller('OrganizerAccountCtrl', OrganizerAccountCtrl);

  OrganizerAccountCtrl.$inject = ['$scope','$modal','$http','$location','$timeout','Authentication','Organizer'];
  /**
  * @namespace RegisterController
  */
  function OrganizerAccountCtrl($scope,$modal,$http,$location,$timeout,Authentication,Organizer) {


    var vm = this;
    activate();

    var cache_organizer = Authentication.getAuthenticatedAccount();
    vm.organizer    = new Organizer(cache_organizer);

    vm.errors = {};
    vm.password_data = {};
    
    

    vm.isCollapsed  = true;

    //submit callbacks
    vm.changeEmail    =  _changeEmail;

    vm.changePassword =  _changePassword;
    
    



    //Private functions

    function _changeEmail() {
      _clearErrors(vm.account_form_email);
      vm.organizer.change_email()
        .success(_changeSuccess)
        .error(_changeFail);

    }



    function _changePassword() {
      _clearErrors(vm.account_form_password);
      vm.organizer.change_password(vm.password_data)
        .success(_changePasswordSuccess)
        .error(_changeFail);
      
    }

    //Handle responses
    function _changeSuccess(response){

      Authentication.updateAuthenticatedAccount();
      _toggleMessage();

    }

    //Handle responses
    function _changePasswordSuccess(response){

      //$location.url('/');
      window.location = '/';

    }


    function _changeFail(response){

      if (response['form_errors']) {

        angular.forEach(response['form_errors'], function(errors, field) {

          _addError(field, errors[0]);

        });

      }
    }


    function _clearErrors(form){
      form.$setPristine();
      vm.errors = null;
      vm.errors = {};
    }



    function _addError(field, message) {

      vm.errors[field] = message;
      if (field in vm.account_form_email)
        vm.account_form_email[field].$setValidity(message, false);

      if (field in vm.account_form_password)
        vm.account_form_password[field].$setValidity(message, false);

    };


    function _toggleMessage(){
      vm.isCollapsed  = false;
      var timer = $timeout(function() {
         vm.isCollapsed = true;
      }, 1000);
    }


    function activate() {
      // If the user is authenticated, they should not be here.
      if (!(Authentication.isAuthenticated())) {
        $location.url('/');
      }
    }

  };

  })();