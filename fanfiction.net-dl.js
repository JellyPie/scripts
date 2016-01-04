javascript:(function(){
for (var i = 0, hrs = document.getElementsByTagName('hr'); i < hrs.length; i++) {
    var p = document.createElement('p');
    var txt = document.createTextNode('---');
    p.appendChild(txt);
    hrs[i].parentNode.replaceChild(p,hrs[i])
}

var story = document.getElementById('storytext').innerText;
window.open(encodeURI('data:text/plain,'+story));
})();
