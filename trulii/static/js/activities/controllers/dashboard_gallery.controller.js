/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('ActivityDBGalleryController', ActivityDBGalleryController);

  ActivityDBGalleryController.$inject = ['$scope','$state','$timeout','$q','$modal','$stateParams','activity','UploadFile'];
  /**
  * @namespace ActivityDBGalleryController
  */
  function ActivityDBGalleryController($scope,$state,$timeout,$q,$modal,$stateParams,activity,UploadFile) {




    var vm = this;

    //console.log(ActivityDashboardCtrl,"parent");
    console.log($scope.pc,"padre");

    initialize();


    vm.activity = angular.copy(activity);

    vm.addImage = _addImage;

    vm.deleteImage = _deleteImage;

    vm.save_activity = _updateActivity;

    vm.setOverElement = _setOverElement;

    vm.showTooltip = _showTooltip;



    /******************ACTIONS**************/


    
    function _addImage(images){

      //vm.images.concat(images.pop());
      _clearErrors();
      vm.uploading_photo = images.pop();
      //vm.photos.push(images.pop());
      if(vm.uploading_photo)
        activity.addPhoto(vm.uploading_photo,vm.upload_url)
          .then(_successUploaded,_erroredUpload,_progressUpload);

      //console.log("UPLOAD IMAGE",vm.images);

      //vm.images.push(photo);

    }

    function _deleteImage(image){


      var modalInstance = $modal.open({
        templateUrl:  'static/partials/activities/messages/confirm_delete_image.html',
        controller: 'ModalInstanceCtrl',
        size: 'lg',
      });

      modalInstance.result.then(function(){

        

        activity.deletePhoto(image)
          .then(_successDelete,_erroredDelete)


      });







    }


    function _updateActivity() {
      _clearErrors();
      vm.activity.update()
          .success(function(response){
              vm.isCollapsed = false;
              angular.extend(activity,vm.activity);
              $scope.pc.activitySectionUpdated(response);
          })
          .error(_errored);
    }

    function _showTooltip(element){
        
      if (vm.currentOverElement==element)
          return true
      return false
    }


    function _setOverElement(element){

        vm.currentOverElement = element;
    }

    /*****************SETTERS********************/




    /*********RESPONSE HANDLERS***************/


    function _successUploaded(response){
        vm.photo_loading = false;
        vm.images.push(response.data.photo);
        
        $scope.pc.activitySectionUpdated(response.data.activity);

    }

    function _progressUpload(response){
      vm.photo_loading = true;
    }

    function _erroredUpload(response){
      vm.photo_loading = false;
      var data = response.data;
      if (data['errors']) {
        
        angular.forEach(data['errors'], function(errors) {

          _addError(errors.field,errors.errors[0]);   

        });

      }
      else{

        angular.forEach(data, function(message,field) {

          _addError(field,message[0]);   

        });


      }
    }

    function _successDelete(response){

      var image_id = response.data.photo_id;
      var images   = angular.copy(vm.images);

      angular.forEach(images,function(photo,index){

          if (photo.id == image_id){
              vm.images.splice(index,1);
          }

      }); 
      $scope.pc.activitySectionUpdated(response.data.activity);

      // activity.load().then(function(data){

      //   $scope.pc.activitySectionUpdated(response);

      // });

      

    }

    function _erroredDelete(response){

      angular.forEach(response.data, function(message,field) {

        _addError(field,message[0]);   

      });

    }


    function _clearErrors(){
        //vm.activity_detail_form.$setPristine();
        vm.errors = null;
        vm.errors = {};
    }



    function _addError(field, message) {
      vm.errors[field] = message;

    };

    function _errored(errors) {


    }


    function activate() {
      // If the user is authenticated, they should not be here.

    }

    function initialize(){

        vm.errors = {};
        vm.isCollapsed = true;
        vm.uploading_photo = false;
        vm.images = activity.photos;


    }

  };

  })();