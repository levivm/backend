/**
* Register controller
* @namespace thinkster.organizers.controllers
*/
(function () {
  'use strict';


  angular
    .module('trulii.activities.controllers')
    .controller('TimePickerController', TimePickerController);

  TimePickerController.$inject = ['$scope','activity'];
  /**
  * @namespace TimePickerController
  */
  function TimePickerController($scope,activity) {

      $scope.mytime = new Date();  

      $scope.mytime2 = new Date();
      
      $scope.hstep = 1;
      $scope.mstep = 15;

      $scope.options = {
        hstep: [1, 2, 3],
        mstep: [1, 5, 10, 15, 25, 30]
      };

      $scope.ismeridian = true;
      $scope.toggleMode = function() {
        $scope.ismeridian = ! $scope.ismeridian;
      };

      $scope.update = function() {
        var d = new Date();
        d.setHours( 14 );
        d.setMinutes( 0 );
        $scope.mytime = d;
      };

      $scope.changed = function () {
        if($scope.mytime > $scope.mytime2){
          $scope.mytime = $scope.mytime2;
          alert('Tus horas fueron modificadas. Tu hora de inicio de sesión debe ser menor a tu hora de fin de sesión.');
        };
      };

      $scope.changed2 = function(){
        if($scope.mytime > $scope.mytime2){
          $scope.mytime = $scope.mytime2;
          alert('Tus horas fueron modificadas. Tu hora de inicio de sesión debe ser menor a tu hora de fin de sesión.');
        };
      };
      $scope.clear = function() {
        $scope.mytime = null;
      };

     
      /*$scope.$watch('mytime', function(value){
        if($scope.mytime > $scope.mytime2) 
          alert("!");
      });*/
      $scope.$watch('mytime', function(value){
      //  if($scope.mytime > $scope.mytime2) 
          //alert("!");

      });
  }
    
/*
    var timepicker = angular.module('trulii.activities.controllers');
    timepicker
    .controller('TimepickerCtrl', function($scope, $log){
      $scope.mytime = new Date();  
      $scope.objects = [{}];
      alert(":");
    $scope.add_object = function() {
        $scope.objects.push({});  
    };
      $scope.hstep = 1;
      $scope.mstep = 15;
      $scope.options = {
        hstep: [1, 2, 3],
        mstep: [1, 5, 10, 15, 25, 30]
      };
      $scope.ismeridian = true;
      $scope.toggleMode = function() {
        $scope.ismeridian = ! $scope.ismeridian;
      };
      $scope.update = function() {
        var d = new Date();
        d.setHours( 14 );
        d.setMinutes( 0 );
        $scope.mytime = d;
      };
      $scope.changed = function () {
        $log.log('Time changed to: ' + $scope.mytime);
      };
      $scope.clear = function() {
        $scope.mytime = null;
      };
      
    });*/




  })();