let app = {};

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
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    
    app.create_group = function () {
        console.log('create group func'); 
        // console.log(app.vue.rows);  
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

    app.methods = {
        create_group: app.create_group, 
        add_player: app.add_player, 

    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
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
    app.init();
};

init(app);
