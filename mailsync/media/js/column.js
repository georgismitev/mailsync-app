(function($){
  SelectView = Backbone.View.extend({
    events: {
      "change": "selectChanged",
      "focus": "setOld",
    },

    setOld: function() {
      this.oldValue = this.$el.val();
    },

    selectChanged: function(e) {
      this.$el.trigger("changed", [this.oldValue]);
      this.setOld();
    },
  });

  SelectViews = Backbone.View.extend({
    el: "body",

    events: {
      "changed select": "updateSelectedAttributes",
      "submit form#columns-form": "onSubmit",
    },

    onSubmit: function() {
      return this.$("select option[value='email-default']:selected").size() === 1;
    },

    initialize: function() {
      this.render();
      
    },

    render: function() {
      this.$("select").each(function(){
        var select = new SelectView({
          el: this
        });
        
        select.render();

        select.$el.chosen({
          allow_single_deselect: true,
          disable_search_threshold: 100,
        });
      });

      var message = $("#tmpl-message").html();
      window.message.show_message(message, "info");
    },

    clearValueAttribute: function(oldValue){
      this.$("input[id='" + oldValue + "']").val("");
    },

    updateSelectedAttributes: function(e, oldValue) {
      var select = $(e.currentTarget); 
      var value = select.val();

      if (value === "select-field") {
        this.clearValueAttribute(oldValue);
        if (oldValue === "email-default"){
          this.$("input[type='submit']").hide();
        }
        return;
      }

      var alreadySelected = this.$("select option[value=" + value + "]:selected").size();
      
      if (alreadySelected > 1) {
        select.val(oldValue);
        select.val("").trigger("liszt:updated");
        return;
      }

      this.clearValueAttribute(oldValue);

      var columnName = select.parent().find("span.column-name").html();
      this.$("input[id='" + value + "']").val(columnName);

      if (value === "email-default"){
        this.$("input[type='submit']").show();
        window.message.hide_message(message, "info");
      }
    }

  });

  window.view = new SelectViews;
  
})(jQuery);