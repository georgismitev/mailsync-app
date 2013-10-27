(function($){

  var mysql_defaults = {
    port: "3066", 
    username: "root", 
    host: "localhost"
  }

  var postgres_defaults = {
    port: "5432", 
    username: "postgres", 
    host: "localhost"
  }

  DatabaseModel = Backbone.Model.extend();

  DatabaseView = Backbone.View.extend({

    el: $("#drivers-form"),
    
    events: {
      "change #driver": "update_driver_form",
      "click #checkconnection": "checkDatabaseConnection",
      "tableschanged": "onChosenChanged",
      "tablesloaded": "showTables",
    },
        
    initialize: function() {
      this.update_driver_form();
      this.base_url = getBaseUrl();

      $("#driver").chosen({disable_search_threshold: 100});
    },

    onChosenChanged: function(e, table) {
      $(".button-submit").show();
    },

    hideTablesContainer: function() {
      this.$("#tables-container").hide();
      $(".button-submit").hide();
    },

    showTables: function(e, tables_data) {
      var container = $("#tables-container");
      var compiledTmpl = _.template($("#tmpl-tables").html(), { tables: tables_data });
      
      container.html(compiledTmpl);
      $("#tables").chosen();
      
      if (!container.is(":visible")) container.show();
      $(".loader").spin(false);
      
      var form = this;

      $("#drivers-form").on("change", "#tables", function() {
        form.$el.trigger("tableschanged", [this.value]) 
      });
    },

    update_driver_form: function() {
      driver = $("#driver").val();

      driver_details = (driver === "mysql")? mysql_defaults : postgres_defaults;
      
      $("#drivers-form :input").each(function(){
        element = $(this).attr("id");
        
        if(element in driver_details){ 
          $(this).val(driver_details[element]);
        }
      });

      this.hideTablesContainer();
    },

    checkDatabaseConnection: function(event) {
      prepareAjaxCall();

      spinner_options.left = "-165px";
      spinner_options.top = "12px";
      
      $(".loader").spin(spinner_options);
      var driversForm = form2object("drivers-form", ".", false, null, false);

      this.model = new DatabaseModel({
        "connection_details": driversForm["driver"]
      });

      this.model.url = "/database/tables";
      var form = this;

      this.model.save({}, {
        success: function(model, response) {
          if (response.status == "ok") {
            window.message.hide_message();
            
            form.$el.trigger("tablesloaded", [response.data]);
          }
          else if (response.status == "error") {
             window.message.show_message(response.data);

             $(".loader").spin(false);
          }
        },
      }); 
    }
  
  });

  window.database_view = new DatabaseView;

})(jQuery);