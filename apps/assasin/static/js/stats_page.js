let app = {};

let init = (app) => {
  app.data = {
    statistics: [],
    leaderboard: [],
    players: [],
    currentPlayerID: null,
    currentPlayerKills: 0,
    currentPlayerGamesSurvived: 0,
  };

  app.methods = {
    updateStatistics: function () {
      axios
        .get(get_statistics_url)
        .then(function (response) {
          app.vue.statistics = response.data.statistics;
        })
        .catch(function (error) {
          console.log(error);
        });
    },

    updateLeaderboard: function () {
      axios
        .get(get_leaderboard_url)
        .then(function (response) {
          app.vue.leaderboard = response.data.leaderboard;
        })
        .catch(function (error) {
          console.log(error);
        });
    },

    submitUpdateForm: function () {
      axios
        .post(update_statistics_url, {
          player_id: app.vue.currentPlayerID,
          kills: app.vue.currentPlayerKills,
          games_survived: app.vue.currentPlayerGamesSurvived,
        })
        .then(function (response) {
          app.methods.updateStatistics();
          app.methods.updateLeaderboard();
        })
        .catch(function (error) {
          console.log(error);
        });
    },
  };

  app.vue = new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    data: app.data,
    methods: app.methods,
  });

  app.methods.updateStatistics();
  app.methods.updateLeaderboard();
};

init(app);
