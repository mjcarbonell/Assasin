let app = {};

let init = (app) => {
  // This is the Vue data.
  app.data = {
    rows: [], // rows are the auth.users in the database
    players: [],
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
      app.vue.currentUser = response.data.currentUser;
      axios.get(get_groups_url).then(function (response) {
        //SECOND THEN
        app.vue.groups = app.enumerate(response.data.groups);
        console.log("PLAYERS");
        console.log(app.vue.players);
        console.log("GROUPS");
        console.log(app.vue.groups);
      });
    });
  };
  app.init();
};

init(app);
