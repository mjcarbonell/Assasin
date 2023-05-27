// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete.
        comment_list: [],
        new_comment: "", // JS VARIABLE. Reflects in real time the contents of the input field 
    };

    app.add_comment = function () {
        app.vue.comment_list.push(app.vue.new_comment); // PUSHING CURRENT INPUT FIELD 
        app.vue.new_comment = ""; // RESETTING INPUT FIELD TO EMPTY STRING AFTER WE ADDED OUR COMMENT AND FINISHED 
        // PRESSING THE BUTTON 
    };

    app.methods = {
        // Complete.
        add_comment: app.add_comment,
    };

    // This creates the Vue instance. VUE OBJECT 
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        // Do any initializations (e.g. networks calls) here.
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
