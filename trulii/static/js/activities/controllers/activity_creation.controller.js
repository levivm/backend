/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('ActivityCreationCtrl', ActivityCreationCtrl);

  ActivityCreationCtrl.$inject = ['$scope','$modal','$http','$state','$timeout','$q','$stateParams','filterFilter','Authentication','UploadFile','Categories','Activity'];
  /**
  * @namespace RegisterController
  */
  function ActivityCreationCtrl($scope,$modal,$http,$state,$timeout,$q,$stateParams,filterFilter,Authentication,UploadFile,Categories,Activity) {

    activate();
    
    $scope.activity = new Activity();


    var activity_id = $stateParams.activity_id;

    if (activity_id)
        _setUpdate(activity_id);
    else
        _setCreate();
        

    $scope.errors = {};

    _setWatchers();

    $scope.isCollapsed = true;


    function _setUpdate(activity_id){
        $scope.activity.load(activity_id)
            .then($scope.activity.generalInfo,_loadActivityFail)
            .then(_setPreSaveInfo)
            .then(_successLoadActivity);
        $scope.save_activity = _updateActivity;
        $scope.creating = false;
    }


    function _setCreate(){

        $scope.save_activity = _createActivity;
        $scope.creating = true;
        $scope.activity.generalInfo().then(_setPreSaveInfo);


    }

    function _createActivity() {
        _clearErrors();
        _updateTags();
        _updateSelectedValues();
        $scope.activity.create()
            .success(_successCreation)
            .error(_errored);
    }
    
    function _updateActivity() {
        _clearErrors();
        _updateTags();
        _updateSelectedValues();
        $scope.activity.update()
            .success(function(response){
                $scope.isCollapsed = false;
            })
            .error(_errored);
    }



    // //Private functions

    function _setPreSaveInfo(response) {
        $scope.selected_category = {};
        $scope.selected_sub_category = null;
        $scope.selected_type = {};
        $scope.selected_level = {};

        var data = response.data;
            
        var categories = new Categories(data.categories);
        $scope.activity_sub_categories = data.subcategories;
        $scope.activity_categories = categories;
        $scope.activity_types  = data.types;
        $scope.activity_levels = data.levels;


        $scope.selected_sub_category = data.subcategories[0];

        $scope.loadTags = function(){
            var deferred = $q.defer();
                deferred.resolve(data.tags);
            return deferred.promise;
        };


        var deferred = $q.defer();
            deferred.resolve($scope.activity);
        return deferred.promise;

      
    }


    function _successLoadActivity(response){
        $scope.selected_level = filterFilter($scope.activity_levels,{code:response.level})[0];
        $scope.selected_type  = filterFilter($scope.activity_types,{code:response.type})[0];
        $scope.selected_category = filterFilter($scope.activity_categories,{id:response.category_id})[0];
        $scope.activity_tags = response.tags;
    
    }

    function _updateTags(){

        $scope.activity.tags = [];
        angular.forEach($scope.activity_tags,function(value,index){

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
            if (oldCategory!=newCategory && newCategory){
                $scope.activity_sub_categories = newCategory.subcategories;
                if (!(oldCategory) && !$scope.creating){
                     $scope.selected_sub_category = filterFilter(newCategory.subcategories,{id:$scope.activity.sub_category})[0];
                }

            }
            else if (!(newCategory)){
                $scope.activity_sub_categories = [];
                $scope.selected_sub_category   = null;
            }
        });


    }

    
    function activate() {
      // If the user is authenticated, they should not be here.
      if (!(Authentication.isAuthenticated())) {
        $state.go('home');
      }
    }

    function _loadActivityFail(response){
        $state.go('home');
        var deferred = $q.defer();
            deferred.reject( response );
            return deferred.promise
    }



    function _clearErrors(){
        $scope.activity_create_form.$setPristine();
        $scope.errors = null;
        $scope.errors = {};
    }



    function _addError(field, message) {
      $scope.errors[field] = message;
      $scope.activity_create_form[field].$setValidity(message, false);

    };

    function _errored(errors) {
        angular.forEach(errors, function(message,field) {


          _addError(field,message[0]);   

        });

    }

    function _successCreation(response){

        $state.go('activties-edit',{id:response.id});
    }


  };

  })();