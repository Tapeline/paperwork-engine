{#
  table-wrap.js — ES3-compliant
  Wraps all tables inside .pw-card with a .pw-table-wrap div
  so they can scroll horizontally on narrow screens.
  Run after DOM is ready.
#}

(function() {

  function addEvent(el, evt, fn) {
    if (el.addEventListener) {
      el.addEventListener(evt, fn, false);
    } else if (el.attachEvent) {
      el.attachEvent("on" + evt, fn);
    }
  }

  function wrapTables() {
    var cards = document.getElementsByClassName
      ? document.getElementsByClassName("pw-card")
      : [];

    for (var c = 0; c < cards.length; c++) {
      var tables = cards[c].getElementsByTagName("table");
      /* Walk backwards because wrapping mutates the live collection */
      for (var t = tables.length - 1; t >= 0; t--) {
        var table = tables[t];
        /* Skip if already wrapped */
        if (table.parentNode && table.parentNode.className &&
            table.parentNode.className.indexOf("pw-table-wrap") > -1) {
          continue;
        }
        var wrapper = document.createElement("div");
        wrapper.className = "pw-table-wrap";
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
      }
    }
  }

  if (document.readyState === "complete" || document.readyState === "interactive") {
    wrapTables();
  } else {
    addEvent(document, "DOMContentLoaded", wrapTables);
  }
})();
