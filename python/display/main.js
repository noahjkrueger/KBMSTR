
// eel.expose(read_data);
const og_layout = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./";
read_data("test", "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./", "~!@#$%^&*()_+QWERTYUIOp{}|ASDFGHJKL:\"ZXCVBNM<>?", "none", 0, "none");
function read_data(kb_name, kb_layout, alt_kb_layout, kb_last_analysis, kb_efficiency, kb_datasets) {
    document.getElementById("keyboard-name").innerText = "The " + kb_name + " keyboard";
    
    let keyboard_div = document.getElementById("keyboard");
    
    let keyrow_1 = document.createElement("div");
    let keyrow_2 = document.createElement("div");
    let keyrow_3 = document.createElement("div");
    let keyrow_4 = document.createElement("div");
    let keyrow_5 = document.createElement("div");
    
    keyrow_1.classList.add("keyrow");
    keyrow_2.classList.add("keyrow");
    keyrow_3.classList.add("keyrow");
    keyrow_4.classList.add("keyrow");
    keyrow_5.classList.add("keyrow");
    
    keyboard_div.appendChild(keyrow_1);
    keyboard_div.appendChild(keyrow_2);
    keyboard_div.appendChild(keyrow_3);
    keyboard_div.appendChild(keyrow_4);
    keyboard_div.appendChild(keyrow_5);

    function create_keys(x, y, row) {
        let count = x;
        for (let cc of kb_layout.substring(x, y)) {
            let og = og_layout.substring(count, count+1);
            let alt = alt_kb_layout.substring(count, count+1);
            let keyy = document.createElement("div");
            let char1 = document.createElement("div");
            keyy.setAttribute("key_map", og+(alt_kb_layout.charAt(kb_layout.indexOf(og))));
            if (og ==='\\') {
                keyy.setAttribute("key_map", '|');
            }
            char1.innerText = cc.toUpperCase();
            if (alt.toUpperCase() == cc.toUpperCase()) {
                keyy.classList.add("key");
                keyy.setAttribute("key_char", cc);
            }
            else {
                let char2 = document.createElement("div");
                keyy.classList.add("key_double");
                keyy.setAttribute("key_char", cc+alt);
                char2.innerText = alt; 
                keyy.appendChild(char2);
            }
            keyy.appendChild(char1);
            row.appendChild(keyy);
            count += 1;
        }
    }

    function create_named_key(name, size, row) {
        let k = document.createElement('div');
        k.innerText = name;
        k.classList.add("key");
        k.classList.add(size);
        k.classList.add("keyword");
        k.setAttribute("key_name", name);
        row.appendChild(k);
    }

    create_keys(0, 13, keyrow_1);
    create_named_key("Backspace", "kw1", keyrow_1);
    create_named_key("Tab", "kw1", keyrow_2);
    create_keys(13, 26, keyrow_2);
    create_named_key("CapsLock", "kw2", keyrow_3);
    create_keys(26, 37, keyrow_3);
    create_named_key("Enter", "kw2", keyrow_3);
    create_named_key("Shift", "kw3", keyrow_4);
    create_keys(37, kb_layout.length, keyrow_4);
    create_named_key("Shift", "kw3", keyrow_4);
    create_named_key(" ", "kw4", keyrow_5);
}

function getKey (e) {
    var event_key = e.key;
    var key_inputted = null;
    if (event_key === '\\') {
        return document.querySelectorAll('[key_map="|"]');
    }
    else {
        key_inputted =  document.querySelector('[key_map*="' + event_key + '"]');
        if (!key_inputted) {
            var k = document.querySelectorAll('[key_name="' + event_key + '"]');
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

document.body.addEventListener('keydown', function (e) {
    var key = getKey(e);
    if (!key) {
        return console.warn('No key for', e.keyCode);
    }
    for (let k of key){
        k.setAttribute('data-pressed', 'on');
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

function size () {
    var size = keyboard.parentNode.clientWidth / 61;
    keyboard.style.fontSize = size + 'px';
}

var keyboard = document.querySelector('.keyboard');
window.addEventListener('resize', function (e) {
    size();
});

size();