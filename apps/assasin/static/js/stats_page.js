let app = {};

let init = (app) => {
  // This is the Vue data.
  app.data = {
    rows: [], // rows are the auth.users in the database
    players: [],
    leaderboard: [],
    groups: [],
    nickname: "", // current username
    currentUser: "",
  };

  app.enumerate = (a) => {
    // This adds an _idx field to each element of the array.
    let k = 0;
    a.map((e) => {
      e._idx = k++;
    });
    return a;
  };

  app.methods = {};

  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods,
  });

  app.init = () => {
    axios.get(get_users_url).then(function (response) {
      // FIRST THEN
      app.vue.rows = app.enumerate(response.data.rows);
      app.vue.players = app.enumerate(response.data.players);

      // Fetch the details of the voted player for each player
      for (let player of app.vue.players) {
        if (player.vote !== null) {
          player.vote = app.vue.players.find(
            (p) => p._idx === player.vote._idx
          );
        }
      }

      // Calculate leaderboard based on wins
      app.vue.leaderboard = app.vue.players.sort((a, b) => b.wins - a.wins);

      app.vue.currentUser = response.data.currentUser;
      axios.get(get_groups_url).then(function (response) {
        // SECOND THEN
        app.vue.groups = app.enumerate(response.data.groups);
        console.log("PLAYERS");
        console.log(app.vue.players);
        console.log("GROUPS");
        console.log(app.vue.groups);
        console.log("LEADERBOARD");
        console.log(app.vue.leaderboard);
      });
    });
  };

  app.init();
};

init(app);
