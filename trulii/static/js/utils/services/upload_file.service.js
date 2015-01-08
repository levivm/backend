/**
* Authentication
* @namespace thinkster.authentication.services
*/
(function () {
  'use strict';

  angular
    .module('trulii.utils.services')
    .factory('UploadFile', UploadFile);

  UploadFile.$inject = ['$cookies', '$http','$upload','$window','Authentication'];

  /**
  * @namespace Authentication
  * @returns {Factory}
  */
  function UploadFile($cookies, $http,$upload,$window,Authentication) {
    /**
    * @name UploadFile
    * @desc The Factory to be returned
    */


    var UploadFile = {
      upload_file: upload_file,
      check_file: check_file,
    };



    return UploadFile;


    function check_file(file){

      var helper = {
            //support: !!($window.FileReader && $window.CanvasRenderingContext2D),
            isFile: function(item) {
                return angular.isObject(item) && item instanceof $window.File;
            },
            isImage: function(file) {
                var type =  '|' + file.type.slice(file.type.lastIndexOf('/') + 1) + '|';
                return '|jpg|png|jpeg|bmp|gif|'.indexOf(type) !== -1;
            },
            correctSize: function(file){
                return file.size < 2621440
            }
        };

      return helper.isFile(file[0]) && helper.isImage(file[0]) && helper.correctSize(file[0])

    }

    ////////////////////

    /**
    * @name upload_file
    * @desc Try to upload_file a new user
    * @param {string} username The username entered by the user
    * @param {string} password The password entered by the user
    * @param {string} email The email entered by the user
    * @returns {Promise}
    * @memberOf thinkster.authentication.services.Authentication
    */
    function upload_file(file) {





      return $upload.upload({
        url: '/api/users/upload/photo/', // upload.php script, node.js route, or servlet url
        //method: 'POST' or 'PUT',
        //headers: {'Authorization': 'xxx'}, // only for html5
        //withCredentials: true,
        file: file, // single file or a list of files. list is only for html5
        //fileName: 'doc.jpg' or ['1.jpg', '2.jpg', ...] // to modify the name of the file(s)
        //fileFormDataName: myFile, // file formData name ('Content-Disposition'), server side request form name
                                    // could be a list of names for multiple files (html5). Default is 'file'
        //formDataAppender: function(formData, key, val){}  // customize how data is added to the formData. 
                                                            // See #40#issuecomment-28612000 for sample code

      })

     //  return $http.post('/api/users/upload/photo/', {
     //    //username: username,
     //    photo: file,
     //    user_id: 2,
     //  })
     // .success(function(data, status, headers, config) {
     //                console.log('entre');
     //               //console.log(data);
     //               //console.log(data.form_errors);
     //               //return data
     //  }).error(function(data, status, headers, config) {
     //                console.log("mirame");
     //                console.log(data);
                    
     //  });

    }


  }



})();