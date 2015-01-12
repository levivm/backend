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


    activate();

    var cache_organizer = Authentication.getAuthenticatedAccount();
    $scope.organizer    = new Organizer(cache_organizer);

    $scope.errors = {};
    $scope.password_data = {};
    
    

    $scope.isCollapsed  = true;

    //submit callbacks
    $scope.changeEmail    =  _changeEmail;

    $scope.changePassword =  _changePassword;
    
    



    //Private functions

    function _changeEmail() {
      _clearErrors($scope.account_form_email);
      $scope.organizer.change_email()
        .success(_changeSuccess)
        .error(_changeFail);

    }



    function _changePassword() {
      _clearErrors($scope.account_form_password);
      $scope.organizer.change_password($scope.password_data)
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
      $scope.errors = null;
      $scope.errors = {};
    }



    function _addError(field, message) {

      $scope.errors[field] = message;
      if (field in $scope.account_form_email)
        $scope.account_form_email[field].$setValidity(message, false);

      if (field in $scope.account_form_password)
        $scope.account_form_password[field].$setValidity(message, false);

    };


    function _toggleMessage(){
      $scope.isCollapsed  = false;
      var timer = $timeout(function() {
         $scope.isCollapsed = true;
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