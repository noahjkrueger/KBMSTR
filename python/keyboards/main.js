
eel.expose(read_data);
function read_data(json_name) {
    const path = json_name;
    fetch(path).then((response) => response.json()).then((JSON_data) => {
        let keyboard_name = document.getElementById("keyboard-name");
        keyboard_name.innerText = "The " + JSON_data.name + " keyboard";
        
        let last_analysis = document.getElementById("last-analysis");
        last_analysis.innerText = JSON_data.last_analysis;
    
        let efficiency = document.getElementById("efficiency");
        efficiency.innerText = JSON_data.efficiency;
        
        let dataset_names = document.getElementById("dataset-names");
        for (let dataset of JSON_data.last_analysis) {
            dataset_names.innerText = dataset_names.innerText + "\n" + dataset;
        }
        
        let keyboard_div = document.getElementById("keyboard");
        
        let keyrow_1 = document.createElement("div");
        let keyrow_2 = document.createElement("div");
        let keyrow_3 = document.createElement("div");
        let keyrow_4 = document.createElement("div");
        
        keyrow_1.classList.add("keyrow_1");
        keyrow_2.classList.add("keyrow_2");
        keyrow_3.classList.add("keyrow_3");
        keyrow_4.classList.add("keyrow_4");
        
        keyboard_div.appendChild(keyrow_1);
        keyboard_div.appendChild(keyrow_2);
        keyboard_div.appendChild(keyrow_3);
        keyboard_div.appendChild(keyrow_4);
        
        function create_keys(x, y, row) {
            for (let cc of JSON_data.layout.substring(x, y)) {
                let keyy = document.createElement("kbd");
                keyy.innerText = cc;
                keyy.classList.add("key");
                row.appendChild(keyy);
            }
        
        }
        create_keys(0, 10, keyrow_1);
        create_keys(10, 20, keyrow_2);
        create_keys(20, JSON_data.layout.length, keyrow_3);
        let space = document.createElement("kbd");
        space.classList.add("key");
        space.classList.add("space");
        space.innerText = "space";
        keyrow_4.appendChild(space);
    });
}
