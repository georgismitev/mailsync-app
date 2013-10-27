(function($){
  ListView = Backbone.View.extend({
    el: "#lists-form",

    events: {
      "click li": "liSelected",
      "submit": "onSubmit"
    },

    liSelected: function(e) {
      var li = $(e.target);

      // deselect all, mark them as not selected
      this.$("li").css("border", "none").attr("data-selected", "0");
     
      // mark as selected
      li.css("border", "solid 2px black").attr("data-selected", "1");

      // save the list in the hidden field
      this.$("#listid").val(li.attr("data-listid"));
    },

    onSubmit: function() {
      return this.$("li[data-selected='1']").size() === 1;
    }

  });

  window.view = new ListView;
  
})(jQuery);