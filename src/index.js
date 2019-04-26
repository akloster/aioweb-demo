console.log("Starting up..");
import whatever from "./pyodide/pyodide.js";
import py_code from "./main.py";


window.TimeoutPromise = function (time){
    var promise = new Promise(
        function(resolve,reject){window.setTimeout(
                                 function(){resolve(time)}, time)
        });
    return promise;
}
window.jsfetch = function (url){
    return fetch(url);
}



languagePluginLoader.then(()=>{
    console.log(pyodide.runPython('import sys\nsys.version'));
    pyodide.runPython(py_code);
})
