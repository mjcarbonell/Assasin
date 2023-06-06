
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
        active_group: null,
        game_ended: false, 
        timer: 30, 
        killed: null, 
        winner: null,
        current_assasin: null, 
        has_added: false, 
        called_once: false, 
        assasin_nickname: null, 
        vote_clicked: false, 
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    
    app.check_status = function() {
        let temp = []; 
        axios.get(get_groups_url).then(function (response){
            temp = app.enumerate(response.data.groups);
            for(let g of temp){
                if(g.active==true){
                    Vue.set(app.vue, 'active_group', g); 
                    Vue.set(app.vue, 'current_assasin', app.vue.active_group.current_assasin); 
                    for(let p of app.vue.players){
                        if(p.username == app.vue.current_assasin){
                            Vue.set(app.vue, 'assasin_nickname', p.nickname); 
                        }
                    }
                    break; 
                }
                else{
                    Vue.set(app.vue, 'active_group', null)
                }
            }
            // console.log("HI")
            // console.log(app.vue.active_group); 
        })
    }
    app.start_timer = function () { // we subtract 1 and it is called every second 
        // we end the game and set the active group back to null if timer is 0 
        let temp = []; // will hold copy of players most recent votes
        let total = []; 
        let available_ids = []; 
        if (app.vue.timer == 0 && app.vue.active_group!=null){
            axios.post(set_inactive_url, 
                {
                    group_id: app.vue.active_group.id,

                }).then(function (response){
                    // setting group inactive and game_ended to true 
                    Vue.set(app.vue, 'active_group', null); 
                    Vue.set(app.vue, 'game_ended', true); 
                    axios.get(get_users_url).then(function (newResponse){
                        temp = newResponse.data.players; 
                        for(let p of temp){
                            total.push(p.vote); 
                            available_ids.push(p.id); 
                        }
                       // Assuming 'total' is an array of votes and 'available_ids' is an array of available IDs
                        total = total.filter(vote => available_ids.includes(vote));
                        // console.log("AVAILABLE IDS: ", available_ids); 
                        // console.log(total); 
                        let result = total.reduce((acc, num) => {
                            if (num!=null){
                                acc[num] = (acc[num] || 0) + 1;
                            }
                            return acc;
                        }, {});
                        result = Object.keys(result).reduce((a, b) => result[a] > result[b] ? a : b);
                        for(let p of app.vue.players){
                            if (p.id == result){
                                // killing most voted player
                                Vue.set(app.vue, "killed", p.nickname); 
                                if (p.username == app.vue.current_assasin){
                                    Vue.set(app.vue, 'winner', "Bystanders"); 
                                } 
                                else{ // if assasin wins they get +1 win 
                                    Vue.set(app.vue, 'winner', app.vue.current_assasin); 
                                    console.log("CALLED ONCE: ", app.vue.called_once); 
                                    if (app.vue.called_once == false){
                                        Vue.set(app.vue, 'called_once', true); 
                                        axios.post(add_win_url, 
                                            {
                                                winner: app.vue.current_assasin,
                                            }).then(function (thirdResponse){
                                                console.log('success added vote');
                                        })
                                    }
                                    // console.log("WINNER"); 
                                    // console.log(p); 
                                }
                            }
                        }
                    })
                })
        }
        else{
            if (app.vue.timer > 0){
                Vue.set(app.vue, 'timer', app.vue.timer - 1);
            }
        }
    }
    app.vote = function (voted_player, vote_nickname) { // if user refreshes than they have to wait 30 seconds again 
        if (app.vue.timer > 0 && app.vue.active_group != null){ 
            Vue.set(app.vue, 'vote_clicked', true); 
            // player can vot if timer is not zero and active group is still active 
            console.log("voting");
            console.log(voted_player); 
            axios.post(vote_player_url,
                {
                    voted_player: voted_player,
                    currentUser: app.vue.currentUser,
                }).then(function (response){
                    console.log("THENNN"); 
                    for(let p of app.vue.players){
                        if(p.username == app.vue.currentUser){
                            Vue.set(p, 'vote', vote_nickname); 
                        }
                    }
                    console.log(response.voted_player); 
            })
            return; 
        }
        else{
            return; 
        }
    }
   
    app.methods = {
        check_status: app.check_status, 
        start_timer: app.start_timer, 
        vote: app.vote, 
        
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        axios.get(get_users_url).then(function (response){
            // FIRST THEN 
            app.vue.rows = app.enumerate(response.data.rows); 
            app.vue.players = app.enumerate(response.data.players);
            for(let p of app.vue.players){
                Vue.set(p, 'vote', null); 
            }
            app.vue.currentUser = response.data.currentUser; 
            axios.get(get_groups_url).then(function (response){
                //SECOND THEN 
                app.vue.groups = app.enumerate(response.data.groups);
                setInterval(app.check_status, 1000); 
                Vue.set(app.vue, 'timer', 30); 
                setInterval(app.start_timer, 1000); 
            })
        })
    };
    app.init();

};

init(app);
