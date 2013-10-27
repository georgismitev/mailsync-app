(function($){

  MessageModel = Backbone.Model.extend();

  MessageView = Backbone.View.extend({
    // @message -> string
    // @_class - > error, info
    show_message: function(message, _class){
    	$("#message").animate({height: 60}, 100);
    	$('#message').addClass(_class);
      $("#message span").text(message);
    },

    hide_message: function() {
    	$("#message").animate({height: 0}, 100);
    }
  });

  window.message = new MessageView;
  
})(jQuery);
