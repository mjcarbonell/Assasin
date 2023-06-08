
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
        game_started: false, 
        active_group: null 
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    
    app.create_group = function () {
        // Handles creation of new group. It sends POST request to server with current user 
        // as the creator, receives a resposne with new group ID, adds the new group 
        // to the groups array, updates the currentID, updates the player count 
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
                
            })
        // Great. Now the current User is assigned a new group 
        // when they create one. Makes sense. 
    }

    app.add_yourself = function (group_id) {
        // if player is adding themselves and they have a group then delete the old group 
        // This function handles adding the current user to an existing group. 
        // Sends a POST request to the server with group ID and current user, assigns 
        // current user to the group, deletes old group if any, and updates player count 
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
                    app.count_players(); 
                    // console.log(app.vue.groups);
                    // console.log(app.vue.players); 
                })
            
        })

    }
    app.count_players = function () {
        // Function is to update total_players property of each group by iterating through 
        // groups and players arrays, counting the players in each group, and updating the value 
        for(let g of app.vue.groups){
            Vue.set(g, 'total_players', 0); 
            for(let p of app.vue.players){
                if(parseInt(g.id) == parseInt(p.group_id)){
                    newTotal = g.total_players + 1; 
                    Vue.set(g, 'total_players', newTotal); 
                }
            }
        }
    }
    app.start_game = function (group_id) { // setting group to true and all others to false 
        // starts game for specific group and players arrays, counting the playeers 
        // in each group, and updating the value 
        axios.post(set_active_url,
            {
                group_id: group_id,
            }).then(function (response){
        })
        Vue.set(app.vue, 'game_started', true); 
    }
    app.check_status = function() {
        // Function periodically checks status of groups by sending GET request 
        // to the server. It updates the active_group based on the resposne, taking 
        // into account the total player count of the group 
        let temp = []; 
        axios.get(get_groups_url).then(function (response){
            temp = app.enumerate(response.data.groups);
            for(let g of temp){
                if(g.active==true){
                    for(let group of app.vue.groups){
                        if (group.id == g.id){
                            console.log("players: ", group.total_players);
                            if(group.total_players >=3 ){
                                // console.log("enough: ", enoughPlayers); 
                                Vue.set(app.vue, 'active_group', g); 
                                return; 
                            }
                            else{
                                Vue.set(app.vue, 'active_group', null); 
                            }
                        }
                    }
                    // console.log("active group");
                    // console.log(app.vue.active_group); 
                    break; 
                }
                else{
                    Vue.set(app.vue, 'active_group', null); 
                    // console.log("check status"); 
                    // console.log(app.vue.active_group); 
                }
            }
            // if we checked all groups and none were active we do not have an active_group
        })
    }
   
    app.methods = {
        create_group: app.create_group, 
        add_yourself: app.add_yourself, 
        count_players: app.count_players,
        start_game: app.start_game, 
        check_status: app.check_status, 
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

            axios.get(get_groups_url).then(function (secondResponse){
                app.vue.groups = app.enumerate(secondResponse.data.groups);
                for(let g of app.vue.groups){
                    Vue.set(g, 'active', false);
                }
                app.count_players(); 
            })
        })
        setInterval(app.check_status, 2000);        
    };
    app.init();
};


init(app);
