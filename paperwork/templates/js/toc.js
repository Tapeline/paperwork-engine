{#
  toc.js — ES3-compliant tree collapse/expand logic
  Handles the expandable TOC trees in both sidebars.
#}

(function() {

  /* --- CSS class helpers (ES3, no classList) --- */
  function hasClass(el, cls) {
    return (" " + el.className + " ").indexOf(" " + cls + " ") > -1;
  }

  function addClass(el, cls) {
    if (!hasClass(el, cls)) {
      el.className = el.className ? el.className + " " + cls : cls;
    }
  }

  function removeClass(el, cls) {
    var re = new RegExp("(^|\\s)" + cls + "(\\s|$)", "g");
    el.className = el.className.replace(re, " ").replace(/^\s+|\s+$/g, "");
  }

  function toggleClass(el, cls) {
    if (hasClass(el, cls)) {
      removeClass(el, cls);
    } else {
      addClass(el, cls);
    }
  }

  function addEvent(el, evt, fn) {
    if (el.addEventListener) {
      el.addEventListener(evt, fn, false);
    } else if (el.attachEvent) {
      el.attachEvent("on" + evt, fn);
    }
  }

  /**
   * Initialize all TOC trees on the page.
   * Attaches click handlers to .pw-toc-toggle buttons.
   */
  function initTocTrees() {
    var toggles = document.getElementsByClassName
      ? document.getElementsByClassName("pw-toc-toggle")
      : getElementsByClassNameCompat("pw-toc-toggle");

    for (var i = 0; i < toggles.length; i++) {
      (function(btn) {
        addEvent(btn, "click", function(e) {
          /* Prevent navigation if the toggle is inside a link */
          if (e && e.preventDefault) {
            e.preventDefault();
          }
          /* Toggle the parent .pw-toc-item */
          var item = btn.parentNode;
          if (item && hasClass(item, "pw-toc-item")) {
            toggleClass(item, "is-expanded");
          }
        });
      })(toggles[i]);
    }
  }

  /**
   * Expand tree nodes leading to the currently active link.
   * Looks for .pw-toc-link.is-active and expands all ancestor nodes.
   */
  function expandActiveNodes() {
    var activeLinks = document.getElementsByClassName
      ? document.getElementsByClassName("is-active")
      : getElementsByClassNameCompat("is-active");

    for (var i = 0; i < activeLinks.length; i++) {
      var node = activeLinks[i].parentNode;
      while (node) {
        if (node.className && hasClass(node, "pw-toc-item")) {
          addClass(node, "is-expanded");
        }
        node = node.parentNode;
      }
    }
  }

  /**
   * Fallback for getElementsByClassName (IE8 and older).
   */
  function getElementsByClassNameCompat(cls) {
    var results = [];
    var all = document.getElementsByTagName("*");
    for (var i = 0; i < all.length; i++) {
      if (hasClass(all[i], cls)) {
        results.push(all[i]);
      }
    }
    return results;
  }

  /* --- Initialize --- */
  function init() {
    initTocTrees();
    expandActiveNodes();
  }

  if (document.readyState === "complete" || document.readyState === "interactive") {
    init();
  } else {
    addEvent(document, "DOMContentLoaded", init);
  }

  /* Expose API */
  window.PaperworkToc = {
    init: init,
    expandActive: expandActiveNodes
  };
})();
