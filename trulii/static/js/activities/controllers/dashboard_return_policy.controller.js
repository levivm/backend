/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('ActivityDBReturnPDashboard', ActivityDBReturnPDashboard);

  ActivityDBReturnPDashboard.$inject = ['$scope','activity'];
  /**
  * @namespace ActivityDBReturnPDashboard
  */
  function ActivityDBReturnPDashboard($scope,activity) {


    $scope.activity = activity;

    initialize();

    $scope.save_activity  = _updateActivity;

    $scope.setOverElement = _setOverElement;

    $scope.showTooltip    = _showTooltip;



    

    /******************ACTIONS**************/


    
    function _updateActivity() {
        console.log($scope.activity);
        $scope.activity.update()
            .success(function(response){
                $scope.isCollapsed = false;
            })
            .error(_errored);
    }

    function _showTooltip(element){

        if ($scope.currentOverElement==element)
            return true
        return false
    }


    function _setOverElement(element){

        $scope.currentOverElement = element;
    }



    /*****************SETTERS********************/





    /*********RESPONSE HANDLERS***************/





    function _clearErrors(){
        $scope.activity_return_policy_form.$setPristine();
        $scope.errors = null;
        $scope.errors = {};
    }



    function _addError(field, message) {
      $scope.errors[field] = message;
      $scope.activity_return_policy_form[field].$setValidity(message, false);

    };

    function _errored(errors) {
        angular.forEach(errors, function(message,field) {


          _addError(field,message[0]);   

        });

    }


    function activate() {

      // If the user is authenticated, they should not be here.

    }

    function initialize(){

        $scope.errors = {};
        $scope.isCollapsed = true;

    }




       

  };

  })();