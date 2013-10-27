(function($){

  ApiModel = Backbone.Model.extend();

  ApiView = Backbone.View.extend({
    el: "#api-form",

    events: {
      "click #checkapi": "getLists",
      "click .radiobuttons": "setAPIKey",
      "listschanged": "onChosenChanged",
      "listsloaded": "showLists"
    },

    initialize: function() {
      this.base_url = getBaseUrl();
      this.setAPIKey();
    },

    hideListsContainer: function() {
      this.$("#lists-container").hide();
      $(".button-submit").hide();
    },

    showLists: function(e, lists) {
      var container = this.$("#lists-container");
      var compiledTmpl = _.template($("#tmpl-lists").html(), { clients_lists: lists });

      container.html(compiledTmpl);
      if (!container.is(":visible")) container.show();

      this.$(".loader").spin(false);
      
      this.$("#lists").chosen();

      var apiForm = this;
      
      $("#api-form").on("change", "#lists", function() {
        var name = apiForm.$("#lists option:selected").text();             
        apiForm.$el.trigger("listschanged", [this.value, name]);
      });
    },

    setAPIKey: function(e){
      current = $("#api-form input[type='radio']:checked").val();

      $(".instructions").hide();

      if(current == "mailchimp") {
        $(".mailchimp-instructions").show();
      }
      else {
        $(".campaign-instructions").show();
      }

      this.hideListsContainer();
    },

    onChosenChanged: function(e, listId, listName) {
      $(".button-submit").show();

      $("#listid").val(listId);
      $("#listname").val(listName);
    },

    getLists: function() {
      prepareAjaxCall();

      var apiForm = form2object("api-form", ".", false, null, false);

      this.model = new ApiModel({
        "api": apiForm["api"]
      });

      this.model.url = "/api/lists";
      $(".loader").spin(spinner_options);

      var form = this;
      
      this.model.save({}, {
        success: function(model, response) {
          if (response.status == "ok") {
            window.message.hide_message();

            form.$el.trigger("listsloaded", [response.data]);
          }
          else if (response.status == "error") {
            window.message.show_message(response.data);

            $(".loader").spin(false);
          }
        },
      }); 
    },

  });

  window.view = new ApiView;
  
})(jQuery);