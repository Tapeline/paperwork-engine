{#
  search.js — ES3-compliant search bar behavior
  Handles the hero search bar and navbar search bar interactions.
  Actual search logic depends on a search index being available
  (see search_index_builder.py). This module provides the UI glue.
#}

(function() {

  function addEvent(el, evt, fn) {
    if (el.addEventListener) {
      el.addEventListener(evt, fn, false);
    } else if (el.attachEvent) {
      el.attachEvent("on" + evt, fn);
    }
  }

  /**
   * Navigate to the search results page with the query as a parameter.
   * @param {string} query
   */
  function performSearch(query) {
    query = query.replace(/^\s+|\s+$/g, ""); /* trim */
    if (!query) return;
    /* Navigate to search.html with query param */
    var baseUrl = document.getElementById("pw-search-base");
    var base = baseUrl ? baseUrl.getAttribute("data-url") : ".";
    window.location.href = base + "/search.html?q=" + encodeURIComponent(query);
  }

  /**
   * Attach submit behavior to a search input.
   * Triggers search on Enter key.
   */
  function bindSearchInput(inputId) {
    var input = document.getElementById(inputId);
    if (!input) return;

    addEvent(input, "keydown", function(e) {
      var key = e.which || e.keyCode;
      if (key === 13) { /* Enter */
        if (e.preventDefault) e.preventDefault();
        performSearch(input.value);
      }
    });
  }

  /**
   * Sync search inputs: typing in one updates the other.
   */
  function syncSearchInputs(id1, id2) {
    var input1 = document.getElementById(id1);
    var input2 = document.getElementById(id2);
    if (!input1 || !input2) return;

    addEvent(input1, "keyup", function() {
      input2.value = input1.value;
    });

    addEvent(input2, "keyup", function() {
      input1.value = input2.value;
    });
  }

  /* --- Initialize --- */
  function init() {
    bindSearchInput("pw-hero-search");
    bindSearchInput("pw-navbar-search");
    syncSearchInputs("pw-hero-search", "pw-navbar-search");
  }

  if (document.readyState === "complete" || document.readyState === "interactive") {
    init();
  } else {
    addEvent(document, "DOMContentLoaded", init);
  }

  window.PaperworkSearch = {
    search: performSearch
  };
})();
