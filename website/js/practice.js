import { generate_kb } from "./keyboard.js";

var praccy = "";
var current_inputted_text = "";
var stated_typing = null;

export async function initPractice() {
    await reload();
    document.getElementById("new-exercise").addEventListener("click", async () => {
        await newExercise();
    });
    document.getElementById("load-preset").addEventListener("click", async () => {
        await reload("preset");
    });
    document.getElementById("load-custom").addEventListener("click", async () => {
        await reload("custom");
    });
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

async function newExercise() {
    var practice_data = null;
    await fetch('./data/practice/practice.json').then(response => response.json()).then(data => {practice_data = data;}).catch((error) => {console.error('Error:', error);});
    praccy = practice_data[String(Math.floor(Math.random() * Object.keys(practice_data).length))];
    current_inputted_text = "";
    stated_typing = null;
    document.getElementById("wpm").innerText = "WPM: 0.00"
    document.getElementById("practice-exercise-correct").innerText = "";
    document.getElementById("practice-exercise-incorrect").innerText = "";
    document.getElementById("practice-exercise-upcoming").innerText = praccy;
    document.documentElement.style.setProperty('--practice-offset', "50%");
}

async function reload(type) {
    const element = document.getElementById("keyboard-practice");
    const physical_layout = document.getElementById('physical-keyboard').value;
    const up_layout = document.getElementById('layout-file');
    const up_config = document.getElementById('config-file');

    await newExercise();

    document.getElementById("practice-exercise-correct").innerText = "";
    document.getElementById("practice-exercise-incorrect").innerText = "";
    document.getElementById("practice-exercise-upcoming").innerText = praccy;

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

function getTime() {
    var tm = new Date();
    return 1000 * ((60 * ((60 * tm.getHours())+ tm.getMinutes()))+ tm.getSeconds()) + tm.getMilliseconds();
}

function typeinBox(key, practice_data, typed) {
    if (!typed) {
        typed = "";
    }
    if (!stated_typing) {
        stated_typing = getTime();
    }
    if (typed === practice_data) {
        return typed;
    }
    const shift = document.querySelector("[data-pressed][practice-key][key_name='Shift']");
    const caps = document.querySelector('[caps-on][practice-key]');
    var input = null;
    if (key.hasAttribute("key_name")) {
        if (key.getAttribute("key_name") === " " || key.getAttribute("key_name") === "Backspace" ) {
            input = key.getAttribute("key_name");
        }
        else {
            return typed;
        }
    }
    else {
        if (shift && caps) {
            input = key.getAttribute('key_char')[0];
        }
        else if (shift || caps) {
            input = key.getAttribute('key_char')[1];
        }
        else {
            input = key.getAttribute('key_char')[0];
        }
    }
    const cur_off = document.documentElement.style.getPropertyValue("--practice-offset");
    var new_off = null;
    if (input === 'Backspace') {
        if (typed.length > 0) {
            typed = typed.substring(0, typed.length - 1);
            new_off = String(parseFloat(cur_off.substring(0, cur_off.length)) + 2.2) + "%";
        }
        else {
            new_off = cur_off
        }
    }
    else {
        typed += input;
        new_off = String(parseFloat(cur_off.substring(0, cur_off.length)) - 2.2) + "%";
    }
    document.documentElement.style.setProperty("--practice-offset", new_off);
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
    const correct = document.getElementById("practice-exercise-correct");
    const incorrect = document.getElementById("practice-exercise-incorrect");
    const upcoming = document.getElementById("practice-exercise-upcoming");
    upcoming.innerText = practice_data.substring(typed.length, practice_data.length);
    correct.innerText = cor;
    incorrect.innerText = typed.substring(x, typed.length);
    document.getElementById("wpm").innerText = "WPM: " + String((typed.length / (5.0 * ((getTime() - stated_typing) / 60000))).toFixed(2));
    return typed;
}