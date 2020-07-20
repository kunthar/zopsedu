var handleDataTableResponsive = function (options) {
    "use strict";
    if ($("#data-table-responsive").length !== 0) {
        $("#data-table-responsive").DataTable({language: options.language, responsive: true})
    }
};
var TableManageResponsive = function () {
    "use strict";
    return {
        init: function (options) {
            handleDataTableResponsive(options)
        }
    }
}();
var handleDataTableButtons = function (options) {
    "use strict";
    0 !== $("#" + options.id).length && $("#" + options.id).DataTable({
        language: options.language,
        dom: "Bfrtip",
        buttons: options.buttons,
        responsive: !0
    })
}, TableManageButtons = function () {
    "use strict";
    return {
        init: function (options) {
            handleDataTableButtons(options)
        }
    }
}();

var handleDataTableButtonsWithoutSearch = function (options) {
    "use strict";
    0 !== $("#" + options.id).length && $("#" + options.id).DataTable({
        language: options.language,
        dom: "Brtip",
        buttons: options.buttons,
        responsive: !0
    })
}, TableManageButtonsWithoutSearch = function () {
    "use strict";
    return {
        init: function (options) {
            handleDataTableButtonsWithoutSearch(options)
        }
    }
}();





var handleDataTableRowReorder = function (options) {
    "use strict";
    0 !== $("#" + options.id).length && $("#" + options.id).DataTable({
        language: options.language,
        responsive: !0,
        rowReorder: !0,
        dom: "Brtip",
    })
}, TableManageRowReorder = function () {
    "use strict";
    return {
        init: function (options) {
            handleDataTableRowReorder(options)
        }
    }
}();