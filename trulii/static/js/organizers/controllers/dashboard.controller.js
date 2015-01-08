/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.organizers.controllers')
    .controller('OrganizerDashboardCtrl', OrganizerDashboardCtrl);

  OrganizerDashboardCtrl.$inject = ['$scope','$modal','$http','$location','Authentication','UploadFile','OrganizerService'];
  /**
  * @namespace RegisterController
  */
  function OrganizerDashboardCtrl($scope,$modal,$http,$location,Authentication,UploadFile,OrganizerService) {


    activate();

    $scope.organizer  = Authentication.getAuthenticatedAccount();
    $scope.photo_path = $scope.organizer.photo;
    $scope.errors = {};
    $scope.photo_invalid = false;
    $scope.photo_loading = false;

    $scope.$watch('organizer.photo', function(old_value,new_value) {

      console.log(old_value);
      console.log(new_value);
      if (old_value!=new_value){ 
        $scope.upload = UploadFile.upload_file($scope.organizer.photo)
          .progress(function(evt) {
            
            console.log('progress evet');
            console.log(evt);
            $scope.photo_loading = true;
        //   console.log('progress: ' + parseInt(100.0 * evt.loaded / evt.total) + '% file :'+ evt.config.file.name);
          })
          .success(_photo_uploaded)
          .error(_errored);
      }

    });

    //submit callbacks
    $scope.submit_info = _update_info;

    




    //Private functions

    function _update_info() {

      // If the user is authenticated, they should not be here.
      var data_info = {
        'name':$scope.organizer.name,
        'bio':$scope.organizer.bio,
        'id':$scope.organizer.id
      }

      OrganizerService.update(data_info)
        .success(_updateSuccess)
        .error(_updateFail);
      
    }

    function _updateSuccess(response){
        Authentication.setAuthenticatedAccount()
    }

    function _updateFail(response){
        console.log(response);
    }

    
    /**
    * @name activate
    * @desc Actions to be performed when this controller is instantiated
    * @memberOf thinkster.authentication.controllers.LoginController
    */
    function activate() {
      // If the user is authenticated, they should not be here.
      if (!(Authentication.isAuthenticated())) {
        $location.url('/');
      }
    }



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

      

      

      if (response['errors']) {
        $scope.photo_invalid = true;
        
        

        angular.forEach(response['errors'], function(errors) {

          _addError(errors.field,errors.errors[0]);   

        });

      }
    }

    function _photo_uploaded(data){
      Authentication.updateAuthenticatedAccount();
      $scope.photo_path    = data.photo;
      $scope.photo_invalid = false;
      $scope.photo_loading = false;
      //console.log('file ' + config.file.name + 'is uploaded successfully. Response: ' + data);

    }

  };

  })();