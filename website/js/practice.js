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
    const w = document.getElementById("practice-exercise-typing").clientWidth;
    document.documentElement.style.setProperty('--practice-font', String(w / 40) + "px");
    document.documentElement.style.setProperty('--practice-offset', String(w / 2) + "px");
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
    try { 
        var alt_string = "";
        for (let c of layout.layout) {
            for (let [k, v] of Object.entries(config.alt_keys)) {
                if (v === c) {
                    alt_string += String(k);
                    break;
                }
            }
        }
        generate_kb("keyboard-practice", (e) => {   
            var key = null;
            if (e.target.innerHTML === "'" || e.target.innerHTML === "\"") {
                key = document.querySelector("[practice-key][key_char*='\"']");
            }
            else if (e.target.innerHTML === "|" || e.target.innerHTML === "\\") {
                key = document.querySelector("[practice-key][key_char*='|']");
            }
            else {
                key = document.querySelector("[practice-key][key_char*='"+ e.target.innerHTML +"']");
            }
            if (key) {
                document.body.dispatchEvent(new KeyboardEvent('keydown', {'key': key.getAttribute("key_map")[0]}));
                document.body.dispatchEvent(new KeyboardEvent('keyup', {'key': key.getAttribute("key_map")[0]}));
            }
            else {
                document.body.dispatchEvent(new KeyboardEvent('keydown', {'key': e.target.innerHTML}));
                document.body.dispatchEvent(new KeyboardEvent('keyup', {'key': e.target.innerHTML}));
            }
        }, "practice-key", physical_layout, layout.layout, alt_string, config.finger_duty);
    }
    catch (error) {
        try {
            var alt_string = "";
            for (let c of config.layout) {
                for (let [k, v] of Object.entries(layout.alt_keys)) {
                    if (v === c) {
                        alt_string += String(k);
                        break;
                    }
                }
            }
            generate_kb("keyboard-practice", null, "practice-key", physical_layout, config.layout, alt_string, layout.finger_duty);
        }
        catch (e) {
            alert("Error loading custom files - malformed or missing. Loading Preset.");
            await reload("preset");
        }
    }
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
    const prac_font_w =  document.documentElement.style.getPropertyValue("--practice-font");
    const delta_margin = 5.0 * parseFloat(prac_font_w.substring(0, prac_font_w.length - 2)) / 8.3;
    const cur_off = document.documentElement.style.getPropertyValue("--practice-offset");
    const cur_off_w = parseFloat(cur_off.substring(0, cur_off.length - 2));
    var new_off = null;
    if (input === 'Backspace') {
        if (typed.length > 0) {
            typed = typed.substring(0, typed.length - 1);
            new_off = String(cur_off_w + delta_margin) + "px";
        }
        else {
            new_off = String(cur_off_w) + "px";
        }
    }
    else {
        typed += input;
        new_off = String(cur_off_w - delta_margin) + "px";
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
    const next = practice_data.substring(typed.length, typed.length + 1);
    const high = document.querySelectorAll('[highlighted]');
    for (let k of high) {
        k.toggleAttribute("highlighted");
    }
    if (x != typed.length) {
        document.querySelector('[practice-key][key_name="Backspace"]').toggleAttribute("highlighted");
    }
    else {    
        if (next === " ") {
            document.querySelector('[practice-key][key_name=" "]').toggleAttribute("highlighted");
        }
        else {
            var k = null;
            if (next === '"') {
                k = document.querySelector('[practice-key][key_char*=\'\"\']');
            } 
            else if (next === "\\") {
                k = document.querySelector('[practice-key][key_char*="\\"]');
            }
            else {
                k = document.querySelector('[practice-key][key_char*="' + next + '"]');
            }
            if (!k) {
                return typed;
            }
            else if (k.getAttribute("key_char")[1] === next) {
                for (let k2 of document.querySelectorAll('[practice-key][key_name="Shift"]')) {
                    k2.toggleAttribute("highlighted");
                }
            }
            k.toggleAttribute("highlighted");
        }
    }
    return typed;
}