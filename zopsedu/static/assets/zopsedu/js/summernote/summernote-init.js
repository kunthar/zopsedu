var handleSummerNote = function (id, options) {
    "use strict";
        $(id).summernote(options);

};
var SummerNoteInit = function () {
    "use strict";
    return {
        init: function (id, options) {
            handleSummerNote(id, options)
        }
    }
}();
