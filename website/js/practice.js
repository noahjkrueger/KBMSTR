import { generate_kb } from "./keyboard.js";

export async function initPractice() {
    await reload();
    document.getElementById("load-preset").addEventListener("click", async () => {
        await reload("preset");
    });
    document.getElementById("load-custom").addEventListener("click", async () => {
        await reload("custom");
    });
    var practice_data = null;
    await fetch('./data/practice/practice.json').then(response => response.json()).then(data => {practice_data = data;}).catch((error) => {console.error('Error:', error);});
    const praccy = practice_data[String(Math.floor(Math.random() * Object.keys(practice_data).length))];
    var current_inputted_text = "";
    document.getElementsByClassName("practice-exercise-upcoming")[0].innerText = praccy;
    document.body.addEventListener('keydown', function (e) {
        var key = getKey(e);
        if (!key) {
            return console.warn('No key for', e.keyCode);
        }
        for (let k of key){
            k.setAttribute('data-pressed', 'on');
            current_inputted_text = typeinBox(k, praccy, current_inputted_text);
        }
    });
    document.body.addEventListener('keyup', function (e) {
        var key = getKey(e);
        if (key) {
            for (let k of key){
                k.removeAttribute('data-pressed');
                if (k.getAttribute("key_name") === "CapsLock") {
                    k.toggleAttribute("caps-on");
                }
            }
        }
    });
}

async function reload(type) {
    const element = document.getElementById("keyboard-practice");

    const physical_layout = document.getElementById('physical-keyboard').value;

    const up_layout = document.getElementById('layout-file');
    const up_config = document.getElementById('config-file');

    var layout = null;
    var config = null;
    if (type === "custom") {
        try {
            layout = await parseJsonFile(up_layout.files[0]);
        }
        catch (error) {
            console.log(error);
            alert("Error loading custom layout - malformed or missing");
            return;
        }
    
        try {
            config = await parseJsonFile(up_config.files[0]);
        }
        catch (error) {
            console.log(error);
            alert("Error loading custom configuration - malformed or missing");
            return;
        }
        if (!layout || !config) {
            alert("Error custom keybaord - you must upload both layout and configuration.");
            return;
        }
    }
    element.innerHTML = "";
    const preset_paths = document.getElementById('preset-keyboard').value.split(" ");
    if (!layout) {
        layout = await fetch(preset_paths[0]).then((response) => response.json()).then((json) => {return json;});
    }
    if (!config) {
        config = await fetch(preset_paths[1]).then((response) => response.json()).then((json) => {return json;});
    }
    var alt_string = "";
    for (let c of layout.layout) {
        for (let [k, v] of Object.entries(config.alt_keys)) {
            if (v === c) {
                alt_string += String(k);
                break;
            }
        }
    }
    generate_kb("keyboard-practice", null, "practice-key", physical_layout, layout.layout, alt_string, config.finger_duty);
}

async function parseJsonFile(file) {
    return new Promise((resolve, reject) => {
      const fileReader = new FileReader()
      fileReader.onload = event => resolve(JSON.parse(event.target.result))
      fileReader.onerror = error => reject(error)
      fileReader.readAsText(file)
    })
  }

function getKey (e) {
    var event_key = e.key;
    var key_inputted = null;
    if (event_key === '\\') {
        return document.querySelectorAll('[practice-key][key_map="|"]');
    }
    else if (event_key === "\"") {
        return document.querySelectorAll("[practice-key][key_map*='\"']");
    }
    else {
        key_inputted =  document.querySelector('[practice-key][key_map*="' + event_key + '"]');
        if (!key_inputted) {
            var k = document.querySelectorAll('[practice-key][key_name="' + event_key + '"]');
            if (!k){
                return null;
            }
            else {
                return k
            }
        }
    }
    return [key_inputted]
}

function typeinBox(key, practice_data, typed) {
    const shift = document.querySelector("[data-pressed][practice-key][key_name='Shift']");
    const caps = document.querySelector('[caps-on][practice-key]');
    var input = null;
    if (key.hasAttribute("key_name")) {
        if (key.getAttribute("key_name") === " " || key.getAttribute("key_name") === "Backspace" ) {
            input = key.getAttribute("key_name");
        }
        else {
            return;
        }
    }
    else if (shift && caps) {
        input = key.getAttribute('key_char')[0];
    }
    else if (shift || caps) {
        input = key.getAttribute('key_char')[1];
    }
    else {
        input = key.getAttribute('key_char')[0];
    }

    const correct = document.getElementById("practice-exercise-correct");
    const incorrect = document.getElementById("practice-exercise-incorrect");
    const upcoming = document.getElementById("practice-exercise-upcoming");

    if (input === 'Backspace') {
        typed = typed.substring(0, typed.length - 1);
    }
    else {
        typed += input;
    }
    var cor = "";
    var x = 0;
    for (let c of typed) {
        if (c === practice_data[x]) {
            cor += c;
        }
        else {
            break;
        }
        x += 1;
    }
    upcoming.innerText = practice_data.substring(typed.length, practice_data.length);
    correct.innerText = cor;
    incorrect.innerText = typed.substring(x, typed.length)
    return typed;
}