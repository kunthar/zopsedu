/*
Template Name: Color Admin - Responsive Admin Dashboard Template build with Twitter Bootstrap 3 & 4
Version: 4.0.0
Author: Sean Ngu
Website: http://www.seantheme.com/color-admin-v4.0/admin/
*/var handleJqueryFileUpload=function(options){$("#fileupload_"+options.id).fileupload({autoUpload:!1,disableImageResize:/Android(?!.*Chrome)|Opera/.test(window.navigator.userAgent),maxFileSize:options.file_size,acceptFileTypes:options.file_types_regex,maxNumberOfFiles:options.maxNumberOfFiles,messages:options.messages,url:options.url}),$.support.cors&&$.ajax({type:"HEAD",url:options.url}).fail(function(){$('<div class="alert alert-danger"/>').text("Upload server currently unavailable - "+new Date).appendTo("#fileupload_"+options.id)})},FormMultipleUpload=function(){"use strict";return{init:function(options){handleJqueryFileUpload(options)}}}();