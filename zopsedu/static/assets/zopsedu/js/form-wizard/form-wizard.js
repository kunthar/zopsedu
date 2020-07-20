var handleFormWizard = function (options) {
    "use strict";
     $(".number-tab-steps").steps(options);
};
var FormWizardInit = function () {
    "use strict";
    return {
        init: function (options) {
            handleFormWizard(options)
        }
    }
}();