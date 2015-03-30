/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.organizers.controllers')
    .controller('OrganizerProfileCtrl', OrganizerProfileCtrl);

  OrganizerProfileCtrl.$inject = ['$scope','$modal','$http','$location','$timeout','Authentication','UploadFile','Organizer'];
  /**
  * @namespace RegisterController
  */
  function OrganizerProfileCtrl($scope,$modal,$http,$location,$timeout,Authentication,UploadFile,Organizer) {

    var vm = this;


    activate();


    var cache_organizer = Authentication.getAuthenticatedAccount();
    
    vm.organizer    = new Organizer(cache_organizer);


    vm.photo_path = vm.organizer.photo;
    vm.errors = {};
    vm.photo_invalid = false;
    vm.photo_loading = false;
    vm.isCollapsed   = true;

    vm.addImage = _uploadImage;





    // vm.$watch('organizer.photo', function(old_value,new_value) {

    //   console.log(old_value,new_value);
    //   if (old_value!=new_value && old_value && new_value){ 
    //     var url = '/api/users/upload/photo/';
    //     console.log("1111111111111111111111111111");
    //     vm.upload = UploadFile.upload_file(vm.organizer.photo,url)
    //       .progress(_progressUpload)
    //       .success(_successUploaded)
    //       .error(_erroredUpload);
    //   }

    // });

    //submit callbacks
    vm.submit_info  =  _update_info;

    vm.submit_video =  _update_video;
    

   


    //Private functions


    function _uploadImage(image){

      var url = '/api/users/upload/photo/';
      UploadFile.upload_file(image,url)
          .progress(_progressUpload)
          .success(_successUploaded)
          .error(_erroredUpload);

    }

    function _update_info() {

      vm.organizer.update()
        .success(_updateSuccess)
        .error(_updateFail);
      
    }


    function _update_video() {


      vm.organizer.update()
        .success(_updateSuccess)
        .error(_updateFail);
      
    }

    function _updateSuccess(response){

      Authentication.updateAuthenticatedAccount();
      _toggleMessage();


    }

    function _updateFail(response){
        console.log(response);
    }

    
    function activate() {
      // If the user is authenticated, they should not be here.
      if (!(Authentication.isAuthenticated())) {
        //$location.url('/');
      }
    }



    function _clearErrors(){
      vm.errors = null;
      vm.errors = {};
    }



    function _addError(field, message) {

      vm.errors[field] = message;

    };

    function _progressUpload(){
      vm.photo_loading = true;
    };


    function _erroredUpload(response) {

      vm.photo_loading = false;
      if (response['errors']) {
        vm.photo_invalid = true; 
        
        

        angular.forEach(response['errors'], function(errors) {

          _addError(errors.field,errors.errors[0]);   

        });

      }
    }

    function _successUploaded(data){
      Authentication.updateAuthenticatedAccount();

      vm.photo_path    = data.photo;
      vm.photo_invalid = false;
      vm.photo_loading = false;

    }

    function _toggleMessage(){


      vm.isCollapsed   = false;
      var timer = $timeout(function() {
        vm.isCollapsed = true;
      }, 1000);
    }

  };

  })();