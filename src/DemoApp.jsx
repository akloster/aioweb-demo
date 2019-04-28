import * as React from "react";
export const DemoApp = (props) => {
    var box;
    if (props.box !== undefined){
     box = <div style={{position:"absolute",
                             top: props.box.top,
                             left: props.box.left}}>
            Hello World
        </div>
    }
    else{
        box = "";
    }
    return <div>
                <h2>aoiaweb demo app</h2>
                <div>
                    {props.status}
                </div>
                {box}
        </div>
}