(function($){

  DashboardModel = Backbone.Model.extend({
    url: "/sync"
  });

  SyncStatusModel = Backbone.Model.extend({
    url: "/sync/status"
  });

  DeleteModel = Backbone.Model.extend();

  DashboardView = Backbone.View.extend({
    el: $("#form_block"),
    
    events: {
      "click .sync-now": "syncNow",
      "click .delete-now": "deleteNow",
      "deleteMessage": "showDeleteMessage",
    },


    showMessage: function(message) {
      $("#message").animate({height: 90}, 5000);
      $("#message span").text(message);
      $("#message").animate({height: 0}, 1000);
    },

    showDeleteMessage: function(e, message) {
      this.showMessage(message);
    },

    syncNow: function(e) {
      var id = $(e.currentTarget).attr("data-id");

      prepareAjaxCall();

      this.syncmodel = new SyncStatusModel({
        "idAttribute": id
      });

      this.model = new DashboardModel({
        "idAttribute": id
      });

      this.model.save({}, {
        success: function(model, response) {
          $(e.currentTarget).text("Importing ...").show();
          $("#progress").animate({height: 90}, 1000);
        },
      });

      var syncmodel = this.syncmodel;
      var self = this;
      
      syncStatusInterval = setInterval(function(){ 
          syncmodel.save({}, {
            success: function(model, response) {
              if (response.status != "error") {
                $("#status").animate({width: response.progress + "%"}, 1000);

                if (response.status === "running")
                {
                  var insertedRows = response.inserted_rows;
                  var rowsToBeInserted = response.rows_to_be_inserted;
                  $("#progress span").text("Syncing: " + insertedRows + " out of " + rowsToBeInserted);
                }
                else if (response.status === "completed") {
                  clearInterval(syncStatusInterval);
                  var parent = $(e.currentTarget).parent();
                  parent.prev().text("0");
                  parent.prev().prev().text(response.last_synced);
                  parent.find(".all_synced").show();
                  $(e.currentTarget).hide();
                  $("#progress span").text(response.message);
                  $("#progress").animate({height: 0}, 1000);
                }
              }
              else { // error
                clearInterval(syncStatusInterval);
                $(e.currentTarget).text("Sync Now");
                self.showMessage(response.message);

                $("#progress").animate({height: 0}, 1000);
              }
            }}); 
        }, 5000);
    },

    deleteNow: function(e) {
      if (confirm("Are you sure?")) {
        var id = $(e.currentTarget).attr("data-id");
        
        prepareAjaxCall();

        this.model = new DeleteModel({
          "id": id
        });

        this.model.url = "/sync/delete/" + id;
        this.model.destroy();

        $(e.currentTarget).parent().parent().remove();

        this.$el.trigger("deleteMessage", ["Sync successfully removed."]);
      }
    }
  
  });

  window.view = new DashboardView;
  
   // Dashboard functions
   $(".tooltip").tooltip({ position: "top center", offset: [-3, 0]});  
  
})(jQuery);