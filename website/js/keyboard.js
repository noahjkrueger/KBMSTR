export function generate_kb(element, onclick, sp_att, og_layout, kb_layout, alt_kb_layout, finger_res) {
    let keyboard_div = document.getElementById(element);
    
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
            keyy.addEventListener("click", onclick);
            if (sp_att) {
                keyy.toggleAttribute(sp_att);
            }
            if (og ==='\\') {
                keyy.setAttribute("key_map", '|');
            }
            else {
                keyy.setAttribute("key_map", og+(alt_kb_layout.charAt(kb_layout.indexOf(og))));
            }
            let char1 = document.createElement("div");
            char1.innerText = cc.toUpperCase();
            keyy.setAttribute("key_char", cc+alt);
            if (alt.toUpperCase() === cc.toUpperCase()) {
                keyy.classList.add("key");
            }
            else {
                let char2 = document.createElement("div");
                keyy.classList.add("key_double");
                char2.innerText = alt; 
                keyy.appendChild(char2);
            }
            keyy.appendChild(char1);
            keyy.classList.add(finger_res[count]);
            row.appendChild(keyy);
            count += 1;
        }
    }

    function create_named_key(name, size, row) {
        let k = document.createElement('div');
        k.addEventListener('click', onclick)
        if (sp_att) {
            k.toggleAttribute(sp_att);
        }
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