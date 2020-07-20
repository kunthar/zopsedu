var handleJstreeCheckable = function(data) {
    $('#jstree-checkable').jstree({
        'plugins': ["wholerow", "checkbox", "types"],
        'core': {
            "themes": {
                "responsive": true
            },
            'data': data
        },
        "types": {
            "default": {
                "icon": "fa fa-key text-success fa-lg"
            },
            "file": {
                "icon": "fa fa-key text-success fa-lg"
            }
        }
    });
};

var TreeView = function () {
    "use strict";
    return {
        //main function
        init: function (data) {
            handleJstreeCheckable(data);
        }
    };
}();
