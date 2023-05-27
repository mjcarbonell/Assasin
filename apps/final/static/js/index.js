// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        rows: [],
        meows: [],
        search_filter: "",
        content: "",
        followList: [],
        current: "",
        currentID: 999, 
        your_feed_status: false, 
        your_meow_status: false, 
        recent_meow_status: true, 
        reply_status: false, 
        reply_owner: "",
        reply_index: undefined, 
        currentUser: "", 
        specific_status: false, 
        specific_name: "", 
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    

    app.clear_search = function () {
        app.vue.search_filter = "";
    };
    
    app.set_follow = function (row_idx) {
        console.log("in set follow");
        // console.log(row_idx); 
        // console.log(app.vue.currentID);
        // console.log(app.vue.rows[row_idx].username);
        
        if (app.vue.rows[row_idx].currentID == app.vue.currentID){
            app.set_unfollow(row_idx); 
            return; 
        }

        axios.post(follow_url,
            {
                user_name: app.vue.rows[row_idx].username,
                uid: app.vue.currentID,
            }).then(function (response) {
                // app.vue.rows[row_idx].currentID = app.vue.currentID; 
                let r = app.vue.rows[row_idx];
                let new_r = {}; 
                new_r.currentID = app.vue.currentID; //currentID is the currentID of the current user setting the follow
                new_r.username = r.username; 
                new_r._idx = row_idx; 
                Vue.set(app.vue.rows, row_idx, new_r);
                // need to vue set the meows of the person followed 
                app.assignMeows(); 
                
        }) 
        console.log("RESPONSE");
        console.log(app.vue.followList);
        console.log(app.vue.rows);
    };

    app.set_unfollow = function (row_idx) {
        console.log("in unfollow");
        let user_name = app.vue.rows[row_idx].username; 
        axios.get(unfollow_url, {params: {user_name: user_name}}).then(function (response){
            let r = app.vue.rows[row_idx];
            let new_r = {};
            new_r.currentID = 999; 
            new_r.username = r.username; 
            new_r._idx = r._idx; 
            Vue.set(app.vue.rows, row_idx, new_r); 
            app.assignMeows();
            console.log("changed");
        })
        // app.init(); 
    }; 

    app.add_meow = function (m) {
        if (m.author != undefined){
            console.log("m exists");
            newContent = "RT " + m.author + ": " + m.content; 
            axios.post(meow_url,
                {
                    user_name: app.vue.rows[app.vue.currentID].username,
                    content: newContent,
                }).then(function (response) {
                    // app.vue.rows[row_idx].currentID = app.vue.currentID; 
                    console.log("done");
                    app.vue.meows.push({
                        author: app.vue.rows[app.vue.currentID].username,
                        content: newContent,
                        timestamp: response.data.ts, 
                        total_replies: parseInt("0"),
                    });
                    app.enumerate(app.vue.meows);
                    app.assignMeows();
                    Vue.set(app.vue, 'content', ''); // Set app.vue.content to an empty string
            })
        }
        else{
            console.log("m does not exist");
            if (app.vue.reply_status == true){ // we are replying 
                console.log("reply is true");
                // let m = app.vue.meows[m._idx];
                
                let first_m = app.vue.meows[app.vue.reply_index]; 
                let new_m = {};
                new_m.currentID = first_m.currentID;  
                new_m.author = first_m.author; 
                new_m.content = first_m.content; 
                new_m.timestamp = first_m.timestamp; 
                new_m.reply_owner = first_m.reply_owner; 
                new_m.total_replies = parseInt(first_m.total_replies) + 1; 
                new_m._idx = first_m._idx; 
                Vue.set(app.vue.meows, new_m._idx, new_m); 
                console.log(app.vue.meows[new_m._idx]);
                axios.post(meow_url,
                    {
                        user_name: app.vue.rows[app.vue.currentID].username,
                        content: app.vue.content,
                        reply_owner: app.vue.reply_index,
                        total_replies: 0,
                    }).then(function (response) {
                        // app.vue.rows[row_idx].currentID = app.vue.currentID; 
                        console.log("done");
                        app.vue.meows.push({
                            author: app.vue.rows[app.vue.currentID].username,
                            content: app.vue.content,
                            timestamp: response.data.ts, 
                            reply_owner: app.vue.reply_index, 
                            total_replies: parseInt("0"),
                        });
                        app.enumerate(app.vue.meows);
                        app.assignMeows();
                        Vue.set(app.vue, 'content', ''); // Set app.vue.content to an empty string
                        console.log(app.vue.meows.slice(-1)[0].content);
                        console.log(app.vue.meows.slice(-1)[0].reply_owner);
                })
            }
            else{ // if we are not replying 
                axios.post(meow_url,
                    {
                        user_name: app.vue.rows[app.vue.currentID].username,
                        content: app.vue.content,
                    }).then(function (response) {
                        // app.vue.rows[row_idx].currentID = app.vue.currentID; 
                        console.log("done");
                        app.vue.meows.push({
                            author: app.vue.rows[app.vue.currentID].username,
                            content: app.vue.content,
                            timestamp: response.data.ts, 
                            total_replies: parseInt("0"),
                        });
                        app.enumerate(app.vue.meows);
                        app.assignMeows();
                        Vue.set(app.vue, 'content', ''); // Set app.vue.content to an empty string
                })
            }
        }
    };

    app.formatTime = function (timestamp) {
        console.log("in format time");
        const now = new Date(Date.now());
        const timestampDate = new Date(timestamp);
        now.setHours(now.getHours() + 7)
        const diff = Math.floor((now - timestampDate) / 1000); // Time difference in seconds
        if (diff < 10) {
        return 'just now';
        } else if (diff < 60) {
        return `${diff} seconds ago`;
        } else if (diff < 3600) {
        const minutes = Math.floor(diff / 60);
        return `${minutes} minutes ago`;
        } else if (diff < 86400) {
        const hours = Math.floor(diff / 3600);
        return `${hours} hours ago`;
        } else {
        const days = Math.floor(diff / 86400);
        return `${days} days ago`;
        }
    };
    
    app.your_feed = function () {
        console.log("HAI");
        console.log(app.vue.your_feed_status);
        let followsNone = true; // assumes they dont follow anyone
        for(let i of app.vue.rows){
            if(i.currentID == app.vue.currentID && i.username != app.vue.currentUser){ // if you find one user that is followed
                console.log("follows atleast one");
                console.log(i.username);
                console.log(i.currentID);
                console.log(app.vue.currentID);
                followsNone = false; 
            }
        }
        if(followsNone == true){ // if they follow none then show recent feed
            Vue.set(app.vue, 'your_feed_status', false);
            Vue.set(app.vue, 'your_meow_status', false);
            Vue.set(app.vue, 'recent_meow_status', true);
            Vue.set(app.vue, 'reply_status', false);
            Vue.set(app.vue, 'specific_status', false);
        }
        else{
            Vue.set(app.vue, 'your_feed_status', true);
            Vue.set(app.vue, 'your_meow_status', false);
            Vue.set(app.vue, 'recent_meow_status', false);
            Vue.set(app.vue, 'reply_status', false);
            Vue.set(app.vue, 'specific_status', false);
        }
        

    } 

    app.your_meows = function () {
        console.log("HAI");
        console.log(app.vue.your_feed_status);
        Vue.set(app.vue, 'your_meow_status', true);
        Vue.set(app.vue, 'your_feed_status', false);
        Vue.set(app.vue, 'recent_meow_status', false);
        Vue.set(app.vue, 'reply_status', false);
        Vue.set(app.vue, 'specific_status', false);
    };
    app.recent_meows = function () {
        console.log("HAI");
        console.log(app.vue.recent_meow_status);
        Vue.set(app.vue, 'recent_meow_status', true);
        Vue.set(app.vue, 'your_meow_status', false);
        Vue.set(app.vue, 'your_feed_status', false);
        Vue.set(app.vue, 'reply_status', false);
        Vue.set(app.vue, 'specific_status', false);
    };

    app.assignMeows = function () {
        console.log("assigning"); 
        for (let i of app.vue.meows) {
            // console.log(i.author);
            for(let k of app.vue.rows) {
                if(i.author == k.username){
                    let m = app.vue.meows[i._idx];
                    let new_m = {};
                    new_m.currentID = k.currentID; 
                    new_m.author = m.author; 
                    new_m.content = m.content; 
                    new_m.timestamp = m.timestamp; 
                    new_m.reply_owner = m.reply_owner; 
                    new_m.total_replies = m.total_replies; 
                    new_m._idx = m._idx; 
                    Vue.set(app.vue.meows, new_m._idx, new_m); 
                }
            }
        }
    }
    app.reply = function (m) {
        console.log("REPLY");
        console.log(m.author);
        Vue.set(app.vue, 'reply_owner', m.author); 
        Vue.set(app.vue, 'reply_index', m._idx)
        Vue.set(app.vue, 'reply_status', true);  // now we only show replies to this post 
        Vue.set(app.vue, 'recent_meow_status', false);
        Vue.set(app.vue, 'your_meow_status', false);
        Vue.set(app.vue, 'your_feed_status', false);
        Vue.set(app.vue, 'specific_status', false);
        console.log(app.vue.reply_index);
        
        // let currentMeow = app.vue.meows[i._idx];
        // let new_m = {};
        // new_m.currentID = currentMeow.currentID; 
        // new_m.author = currentMeow.author; 
        // new_m.content = currentMeow.content; 
        // new_m.timestamp = currentMeow.timestamp; 
        // new_m._idx = currentMeow._idx; 
        // new_m.reply 
        // Vue.set(app.vue.meows, new_m._idx, new_m); 
        

    }
    app.user_feed = function(specific_name) {
        console.log("in hmmm feed");
        Vue.set(app.vue, 'specific_name', specific_name);
        Vue.set(app.vue, 'specific_status', true);
        Vue.set(app.vue, 'reply_status', false);  // now we only show replies to this post 
        Vue.set(app.vue, 'recent_meow_status', false);
        Vue.set(app.vue, 'your_meow_status', false);
        Vue.set(app.vue, 'your_feed_status', false);
    }
    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        clear_search: app.clear_search,
        set_follow: app.set_follow,
        set_unfollow: app.set_unfollow, 
        add_meow: app.add_meow, 
        formatTime: app.formatTime,
        your_feed: app.your_feed,
        your_meows: app.your_meows, 
        recent_meows: app.recent_meows, 
        assignMeows: app.assignMeows, 
        reply: app.reply, 
        user_feed: app.user_feed, 
        
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
        axios.get(get_users_url).then(function (response){
            app.vue.rows = app.enumerate(response.data.rows);
            app.vue.meows = app.enumerate(response.data.meows);
            app.vue.current = response.data.current; 
            app.vue.currentUser = response.data.currentUser; 
            // followList gurantees we get users followed by current user 
            app.vue.followList = app.enumerate(response.data.followList);  
            // Rows is now just all the auth users in database 
            for (let r of app.vue.rows) {
                if (app.vue.current === r.email) {
                    app.vue.currentID = r._idx; // FINDING THE OWNERS INDEX 
                    r.currentID = r._idx; 
                }
            }
            console.log("owner index ");
            console.log(app.vue.currentID);
            //adding those in the following database to the rows. 
            for (let i of app.vue.followList) {
                const existsInRows = app.vue.rows.some((row) => row.username === i.user_name);
                const existingRow = app.vue.rows.find((row) => row.username === i.user_name);
                if (!existsInRows) {
                    // console.log("adding");
                    // console.log(i.user_name);
                  app.vue.rows.push({
                    username: i.user_name,
                    currentID: app.vue.currentID,
                  });
                }
                else{
                    existingRow.currentID = app.vue.currentID;
                }
            }
            for(let i of app.vue.meows){ // every meow intitally gets zero 
                let new_m = {}; // updating count of owner 
                new_m.currentID = i.currentID;  
                new_m.author = i.author; 
                new_m.content = i.content; 
                new_m.timestamp = i.timestamp; 
                new_m.reply_owner = i.reply_owner; 
                new_m.total_replies = parseInt("0") ; 
                new_m._idx = i._idx; 
                Vue.set(app.vue.meows, new_m._idx, new_m);
            }
            
            // counting replies 
            for(let i of app.vue.meows){
                if (parseInt(i.reply_owner) >= 0 ){ // meow has an owner 
                    // find owner of 
                    let currentOwner = app.vue.meows[i.reply_owner];
                    let new_m = {}; // updating count of owner 
                    new_m.currentID = currentOwner.currentID;  
                    new_m.author = currentOwner.author; 
                    new_m.content = currentOwner.content; 
                    new_m.timestamp = currentOwner.timestamp; 
                    new_m.reply_owner = currentOwner.reply_owner; 
                    new_m.total_replies =  parseInt(currentOwner.total_replies) + 1; 
                    new_m._idx = currentOwner._idx; 
                    Vue.set(app.vue.meows, new_m._idx, new_m);
                }
            }
            // for(let i of app.vue.meows){
            //     if(parseInt(i.total_replies) >= 0){
            //         console.log(i); 
            //     }
            // }
            
            app.vue.rows = app.enumerate(response.data.rows); // enumerate rows
            console.log("FIRST");
            // console.log(app.vue.rows);
            // console.log(app.vue.followList);
            app.assignMeows();
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
