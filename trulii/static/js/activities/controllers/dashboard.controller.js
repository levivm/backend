/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('ActivityDashboardCtrl', ActivityDashboardCtrl);

  ActivityDashboardCtrl.$inject = ['$scope','Activity'];
  /**
  * @namespace RegisterController
  */
  function ActivityDashboardCtrl($scope,Activity) {





    var vm = this;

    vm.detailsUpdated = _detailsUpdated;

    vm.detailCompleted = ['content'];

    function _detailsUpdated(data){

        var detailsCompleted;
        angular.forEach(vm.detailCompleted,function(value){

            detailsCompleted = data[value] ? true:false;

            console.log("I jus tupdated updateDetails",data[value]);

        });

        console.log("detailCompleted",detailsCompleted);
    }


    // $scope.isCollapsed = true;

    // function success(){ 

    //   $scope.isCollapsed   = false;

    //   var timer = $timeout(function() {
    //     $scope.isCollapsed = true;
    //   }, 1000);
    // }

    // function _update_info() {

    //   var data_info = {
    //     'name':$scope.organizer.name,
    //     'bio' :$scope.organizer.bio,
    //     'id'  :$scope.organizer.id
    //   }

    //   OrganizerService.update(data_info)
    //     .success(_updateSuccess)
    //     .error(_updateFail);
      
    // }


    // function _update_video() {

    //   var data_info = {
    //     'youtube_video_url':$scope.organizer.youtube_video_url,
    //     'id'  :$scope.organizer.id
    //   }

    //   OrganizerService.update(data_info)
    //     .success(_updateSuccess)
    //     .error(_updateFail);
      
    // }

    // function _updateSuccess(response){

    //   Authentication.updateAuthenticatedAccount();
    //   _toggleMessage();


    // }

    // function _updateFail(response){
    //     console.log(response);
    // }

    
    // function _successUploaded(data){

    //   Authentication.updateAuthenticatedAccount();

    //   $scope.photo_path    = data.photo;
    //   $scope.photo_invalid = false;
    //   $scope.photo_loading = false;

    // }

    // function _toggleMessage(){

    //   $scope.isCollapsed   = false;
    //   var timer = $timeout(function() {
    //     $scope.isCollapsed = true;
    //   }, 1000);
    // }

  };

  })();