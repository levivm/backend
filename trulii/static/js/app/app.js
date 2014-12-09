/*
* app.js
* This file sets global settings
* and set the routing of the app.
*
* deployed
*
*(First part 1):  Sets the CSRF token, this needs angular-cookies.js (This is for is a security mechanism used with django)
*
*(Second part 2): routing for our app. We have two rules:
*
* @ Trulii
* @ Fernando A. Lovera
*/

'use strict';


//(First part 1)

var Activity = angular.module("Activity", []);

Activity.factory('UserService', function() {
    return {
        name : 'anonymous'
    };
});


Activity.run(function ($http, $cookies) {
    $http.defaults.headers.common['X-CSRFToken'] = $cookies['csrftoken'];
})
 
//(2)
Activity.config(function ($routeProvider) {
    $routeProvider
        // "/" : pull the list of all posts
        .when("/", {
            templateUrl: "static/js/app/views/feed.html",
            controller: "FeedController",
            resolve: {
                posts: function (PostService) {
                    return PostService.list();
                }
            }
        })
        // "/post/.id" : the details of a particular post 
        .when("/post/:id", {
            templateUrl: "static/js/app/views/view.html",
            controller: "PostController",
            resolve: {
                post: function ($route, PostService) {
                    var postId = $route.current.params.id
                    return PostService.get(postId);
                }
            }
        })
        .otherwise({
            redirectTo: '/'
        })
})

