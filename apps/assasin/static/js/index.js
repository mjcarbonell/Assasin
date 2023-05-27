// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        rows: [], // rows are the auth.users in the database 
        players: [],
        nickname: "", // current username 
        currentUser: "", 
        inPlayers: false, 
        
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    
    app.create_group = function () {
        console.log('create group func'); 
        console.log(app.vue.rows);  
    }
    app.add_player = function () {
        console.log("add player ");
        axios.post(add_player_url,
            {
                username: app.vue.currentUser,
                nickname: app.vue.nickname,
            }).then(function (response){
                let new_player = {};
                new_player.username = app.vue.currentUser; 
                new_player.nickname = app.vue.nickname;
                new_player.group_id = '';
                new_player.wins = ''; 
                new_player.last_word = '';
                app.vue.players.push(new_player);
                app.enumerate(app.vue.players); 
                Vue.set(app.vue, 'inPlayers', true);
            })

    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        create_group: app.create_group, 
        add_player: app.add_player, 

    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        console.log("init");
        axios.get(get_users_url).then(function (response){
            app.vue.rows = app.enumerate(response.data.rows); 
            app.vue.players = app.enumerate(response.data.players);
            app.vue.currentUser = response.data.currentUser; 
            console.log("pre");
            for(let i of app.vue.players){
                console.log(i); 
                if(i.username == app.vue.currentUser){
                    Vue.set(app.vue, 'inPlayers', true); 
                }
            }
        })
        
        
    };
    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
