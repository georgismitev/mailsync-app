;function getCookie(name) {
  if (document.cookie.length > 0) {
    start = document.cookie.indexOf(name + "=");
    if (start != -1) {
      start = start + name.length + 1;
      end = document.cookie.indexOf(";", start);
      if (end == -1) end = document.cookie.length;
      return unescape(document.cookie.substring(start, end));
    }
  }

  return "";
}

function getBaseUrl() {
  return "127.0.0.1:4321";
}

function prepareAjaxCall() {
  $.ajaxSetup({
    headers: { "X-CSRFToken": getCookie("_xsrf") }
  });
}

var spinner_options = {
  lines: 10, // The number of lines to draw
  length: 4, // The length of each line
  width: 3, // The line thickness
  radius: 5, // The radius of the inner circle
  corners: 1, // Corner roundness (0..1)
  rotate: 0, // The rotation offset
  color: "#237CC7", // #rgb or #rrggbb
  speed: 1, // Rounds per second
  trail: 80, // Afterglow percentage
  shadow: false, // Whether to render a shadow
  hwaccel: true, // Whether to use hardware acceleration
  className: "spinner", // The CSS class to assign to the spinner
  zIndex: 2e9, // The z-index (defaults to 2000000000)
  top: "10px", // Top position relative to parent in px
  left: "-112px" // Left position relative to parent in px
};