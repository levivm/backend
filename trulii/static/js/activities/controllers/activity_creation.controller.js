/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('ActivityCreationCtrl', ActivityCreationCtrl);

  ActivityCreationCtrl.$inject = ['$scope','$modal','$http','$location','$timeout','$q','Authentication','UploadFile','Categories','Activity'];
  /**
  * @namespace RegisterController
  */
  function ActivityCreationCtrl($scope,$modal,$http,$location,$timeout,$q,Authentication,UploadFile,Categories,Activity) {

    activate();



    $scope.activity = new Activity(); 

    $scope.new_activity = _create

    _setPreSaveInfo($scope.activity); 


    _setWatchers();


    function _create() {
        _updateTags();
        _updateSelectedValues();
        $scope.activity.create();
    }
    




    // //Private functions

    function _setPreSaveInfo(activity) {

        activity.generalInfo().success(function(response){
            var categories = new Categories(response.categories);
            $scope.activity_categories = categories;
            $scope.activity_types  = response.types;
            $scope.activity_levels = response.levels; 
            //console.log($scope.activity_levels);

            $scope.loadTags = function(){
                var deferred = $q.defer();
                    deferred.resolve(response.tags);
                return deferred.promise;
            };

        });
      
    }

    function _updateTags(){

        angular.forEach($scope.activity_tags,function(value,index){

            console.log(value,index);
            $scope.activity.tags.push(value.name);
        })
    }


    function _updateSelectedValues(){

        $scope.activity.category = $scope.selected_category.id;
        $scope.activity.sub_category = $scope.selected_sub_category.id;
        $scope.activity.type = $scope.selected_type.code;
        $scope.activity.level = $scope.selected_level.code;


    }

    function _setWatchers(){

        $scope.$watch('selected_category', function (newCategory,oldCategory) {
            if (oldCategory!=newCategory){

                $scope.activity_sub_categories = newCategory.subcategories;
            }
        });

        // $scope.$watch('selected_sub_category', function (newSubCategory,oldSubCategory) {
        //     if (oldSubCategory!=newSubCategory){

        //         //$scope.activity_sub_categories = newSubCategory.subcategories;
        //         $scope.activity.sub_category = newSubCategory.id;
        //         console.log($scope.activity);
        //     }
        // });

        // $scope.$watch('selected_type', function (newType,oldType) {
            
        //     if (newType!=oldType && newType){
        //         $scope.activity.type = newType.code;
        //         console.log($scope.activity);
        //     }
        // });

        // $scope.$watch('selected_level', function (newLevel,oldLevel) {
            
        //     if (newLevel!=oldLevel && newLevel){
        //         $scope.activity.level = newLevel.code;
        //         console.log($scope.activity);
        //     }
        // });



    }

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

    
    function activate() {
      // If the user is authenticated, they should not be here.
      if (!(Authentication.isAuthenticated())) {
        $location.url('/');
      }
    }



    // function _clearErrors(){
    //   $scope.errors = null;
    //   $scope.errors = {};
    // }



    // function _addError(field, message) {

    //   $scope.errors[field] = message;

    // };

    // function _progressUpload(){
    //   $scope.photo_loading = true;
    // };


    // function _erroredUpload(response) {


    //   if (response['errors']) {
    //     $scope.photo_invalid = true;
        
        

    //     angular.forEach(response['errors'], function(errors) {

    //       _addError(errors.field,errors.errors[0]);   

    //     });

    //   }
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