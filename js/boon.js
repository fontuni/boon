/*
 * Copyright (c) 2015, Sungsit Sawaiwan (https://sungsit.com | gibbozer [at] gmail [dot] com).  
 */

// This script aims to fix the lack of language-specific supports for some web browsers.
function langSelector(langs) {
  var elements = document.querySelectorAll(langs);
  var results = [];
  var child;
  for(var i = 0; i < elements.length; i++) {
    child = elements[i].childNodes[0];
    if(elements[i].hasChildNodes() && child.nodeType == 3) {
      results.push(child);
    }
  }
  return results;
}

// This will only work with Thai fonts using FontUni library.
var glyphObj = {
  \u0E0D:"\uF89A",
  \u0E10:"\uF89E",
  \u015E:"\u0218",
  \u015F:"\u0219",
  \u0162:"\u021A",
  \u0163:"\u021B"
};

var glyphReplace = new RegExp(Object.keys(glyphObj).join("|"),"g");

var texts = langSelector('[lang|="pi"], [lang|="sa"], [lang|="ro"], [lang|="mo"]'), _nv;

for (var i = 0, len = texts.length; i<len; i++) {
  _nv = texts[i].nodeValue;
  texts[i].nodeValue = _nv.replace(glyphReplace, function(matched){return glyphObj[matched]});
  
  // debugging
  //console.log(texts[i].nodeValue);
}

// Font switcher
function fontSelector(){
  fontselector = document.getElementById('font-selector');
  fontcanvas = document.getElementsByTagName('body')[0];
  fontclass = fontselector.options[fontselector.selectedIndex].value;
  fontcanvas.className = '';
  fontcanvas.className = fontclass;
}
