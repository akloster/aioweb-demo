console.log("Starting up..");
import whatever from "./pyodide/pyodide.js";
import py_code from "./main.py";
import * as React from "react";
import * as ReactDOM from "react-dom";
import {DemoApp} from "./DemoApp.jsx";



window.TimeoutPromise = function (time){
    var promise = new Promise(
        function(resolve,reject){window.setTimeout(
                                 function(){resolve(time)}, time)
        });
    return promise;
}

window.RequestAnimationFramePromise = function (){
    var promise = new Promise(function(resolve, reject){
        window.requestAnimationFrame(function(timestamp){resolve(timestamp)})
    });
    return promise;
}

window.jsfetch = function (url){
    return fetch(url);
}

window.renderApp = function (props) {
    var component;
    if (props===undefined){
        component = React.createElement("h1", {},"Starting Up...");
    } else {
        component = React.createElement(DemoApp, props);
    }
    ReactDOM.render(component, appElement);
}

window.appElement = document.createElement("div");
document.body.appendChild(appElement);
renderApp();
languagePluginLoader.then(()=>{
    console.log(pyodide.runPython('import sys\nsys.version'));
    pyodide.runPython(py_code);
})
