{#
  sidebar.js — ES3-compliant sidebar toggle logic
  Handles open/close of left and right sidebars on mobile/tablet.
#}

(function() {
  /**
   * Toggle a sidebar panel.
   * @param {string} side - "left" or "right"
   */
  function toggleSidebar(side) {
    var sidebar = document.getElementById("pw-sidebar-" + side);
    var overlay = document.getElementById("pw-sidebar-overlay");
    if (!sidebar) return;

    var isOpen = (" " + sidebar.className + " ").indexOf(" is-open ") > -1;

    if (isOpen) {
      closeSidebar(side);
    } else {
      openSidebar(side);
    }
  }

  function openSidebar(side) {
    var sidebar = document.getElementById("pw-sidebar-" + side);
    var overlay = document.getElementById("pw-sidebar-overlay");
    if (!sidebar) return;
    addClass(sidebar, "is-open");
    if (overlay) addClass(overlay, "is-visible");
  }

  function closeSidebar(side) {
    var sidebar = document.getElementById("pw-sidebar-" + side);
    var overlay = document.getElementById("pw-sidebar-overlay");
    if (!sidebar) return;
    removeClass(sidebar, "is-open");
    if (overlay) removeClass(overlay, "is-visible");
  }

  function closeAllSidebars() {
    closeSidebar("left");
    closeSidebar("right");
  }

  /* --- CSS class helpers (no classList in ES3) --- */
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

  /* --- Wire up event listeners --- */
  function addEvent(el, evt, fn) {
    if (el.addEventListener) {
      el.addEventListener(evt, fn, false);
    } else if (el.attachEvent) {
      el.attachEvent("on" + evt, fn);
    }
  }

  function init() {
    var menuBtn = document.getElementById("pw-navbar-menu-btn");
    var tocBtn = document.getElementById("pw-navbar-toc-btn");
    var overlay = document.getElementById("pw-sidebar-overlay");

    if (menuBtn) {
      addEvent(menuBtn, "click", function() {
        toggleSidebar("left");
      });
    }

    if (tocBtn) {
      addEvent(tocBtn, "click", function() {
        toggleSidebar("right");
      });
    }

    if (overlay) {
      addEvent(overlay, "click", function() {
        closeAllSidebars();
      });
    }
  }

  /* Run on DOM ready */
  if (document.readyState === "complete" || document.readyState === "interactive") {
    init();
  } else {
    addEvent(document, "DOMContentLoaded", init);
  }

  /* Expose for external use if needed */
  window.PaperworkSidebar = {
    toggle: toggleSidebar,
    open: openSidebar,
    close: closeSidebar,
    closeAll: closeAllSidebars
  };
})();
