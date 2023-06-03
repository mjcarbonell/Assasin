
let app = {};


let init = (app) => {

    // This is the Vue data.
    app.data = {
        rows: [], // rows are the auth.users in the database 
        players: [],
        groups: [], 
        nickname: "", // current username 
        currentUser: "", 
        inPlayers: false, 
        currentID: -99, 
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    
    app.create_group = function () {
        console.log('create group func'); 
        // also need to set group_id of currentUser
        axios.post(create_group_url,
            {
                creator: app.vue.currentUser,
            }).then(function (response) {
                console.log("done");
                app.vue.groups.push({
                    creator: app.vue.currentUser, 
                    id: response.data.id
                }); 
                Vue.set(app.vue, 'currentID', response.data.id);  
                app.enumerate(app.vue.groups);
                axios.post(change_id_url,
                    {
                        id: response.data.id,
                        currentUser: app.vue.currentUser,
                    }).then(function (newResponse){
                        for(let p of app.vue.players){
                            if(p.username == app.vue.currentUser){
                                Vue.set(p, 'group_id', response.data.id);
                            }
                        }
                        axios.get(delete_group_url, {params: {username: app.vue.currentUser}}).then(function (response){
                            // now find the old group 
                            for(let g of app.vue.groups){
                                if(g.creator==app.vue.currentUser && g.id != newResponse.data.id){
                                    Vue.delete(app.vue.groups, g._idx);
                                    app.enumerate(app.vue.groups); 
                                }
                            }
                            app.count_players(); 
                            
                        })
                })
                // console.log("refresh")
                // console.log(app.vue.groups);
                // console.log(app.vue.players); 
                // now we update the players adn 
            })
        // Great. Now the current User is assigned a new group 
        // when they create one. Makes sense. 
    }

    app.add_yourself = function (group_id) {
        // if player is adding themselves and they have a group then delete the old group 
        console.log(group_id);
        console.log("ADDING URSELF");
        axios.post(change_id_url,
            {
                id: group_id,
                currentUser: app.vue.currentUser,
            }).then(function (response){
                Vue.set(app.vue, 'currentID', group_id); 
                for(let p of app.vue.players){
                    if(p.username == app.vue.currentUser){
                        Vue.set(p, 'group_id', group_id);
                    }
                }
                axios.get(delete_group_url, {params: {username: app.vue.currentUser}}).then(function (response){
                    console.log(response.message)
                    // now find all groups that the user used to own. They do not own 
                    // anything now that they are in a group 
                    for(let g of app.vue.groups){
                        if(g.creator==app.vue.currentUser){
                            console.log("deleting")
                            console.log(g.id)
                            Vue.delete(app.vue.groups, g._idx);
                            app.enumerate(app.vue.groups); 
                        }
                    }
                    console.log(app.vue.groups);
                    console.log(app.vue.players); 
                })
            app.count_players(); 
        })

    }
    app.count_players = function () {
        console.log(app.vue.groups);
        console.log(app.vue.players);
        for(let g of app.vue.groups){
            Vue.set(g, 'total_players', 0); 
            for(let p of app.vue.players){
                if(parseInt(g.id) == parseInt(p.group_id)){
                    newTotal = g.total_players + 1; 
                    Vue.set(g, 'total_players', newTotal); 
                    console.log("found one");
                }
            }
        }

        console.log("COUNTING")
        console.log(app.vue.groups); 
        
    }


    app.methods = {
        create_group: app.create_group, 
        add_yourself: app.add_yourself, 
        count_players: app.count_players,
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        axios.get(get_users_url).then(function (response){
            app.vue.rows = app.enumerate(response.data.rows); 
            app.vue.players = app.enumerate(response.data.players);
            app.vue.currentUser = response.data.currentUser; 
        })
        axios.get(get_groups_url).then(function (response){
            app.vue.groups = app.enumerate(response.data.groups);
        })
        // console.log(app.vue.players);
        // console.log(app.vue.groups); 
        
        setTimeout(function() {
            app.count_players();
        }, 1000);
       
        
        
    };
    app.init();
   
};


init(app);
