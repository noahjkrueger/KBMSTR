import * as api from './api.js';
import { generate_kb } from './keyboard.js';

function code_key(e) {
    let change_to = document.querySelector("div[selected-finger]");
    let target = e.target;
    if (target.classList.contains("keyword")) {
        return;
    }
    if (target.tagName === "I") {
        target = target.parentNode;
    }
    if (change_to.classList.contains("finger")) {
        target.innerHTML = "<i class='fa-solid fa-fingerprint'></i>";
    }
    else if (change_to.classList.contains("home")) {
        for (let elm of document.getElementsByClassName("key")) {
            if (elm.hasAttribute("finger_home") && elm.getAttribute("finger_home") === change_to.getAttribute("finger")) {
                elm.removeAttribute("finger_home");
                elm.innerHTML = "<i class='fa-solid fa-fingerprint'></i>";
            }
        }
        target.innerHTML = "<i class='fa-solid fa-house'></i>";
        target.setAttribute("finger_home", change_to.getAttribute("finger"));
    }
    target.classList = "key";
    target.classList.add(change_to.getAttribute("finger"));
    target.setAttribute("finger_res", change_to.getAttribute("finger"));
}

export function initConfig() {
    const empty = "                                               ";
    generate_kb("keyboard-configure", code_key, empty, empty, empty, []);
    const config_fingers = document.getElementsByClassName("config-mapping");
    for (let c_fing of config_fingers) {
        c_fing.addEventListener("click", e => {
            let curr = document.querySelector("div[selected-finger]");
            if (curr) {
                curr.toggleAttribute("selected-finger");
            }
            c_fing.toggleAttribute("selected-finger");
        });
    }
    const create_config_button = document.getElementById("create-config-submit");
    create_config_button.addEventListener("click", async (e)=> {
        const alt_keys = {
            ":": ";",
            "~": "`",
            "!": "1",
            "@": "2",
            "#": "3",
            "$": "4",
            "%": "5",
            "^": "6",
            "&": "7",
            "*": "8",
            "(": "9",
            ")": "0",
            "_": "-",
            "+": "=",
            "{": "[",
            "}": "]",
            "|": "\\",
            "<": ",",
            ">": ".",
            "?": "/",
            "\"": "'",
            "A": "a",
            "B": "b",
            "C": "c",
            "D": "d",
            "E": "e",
            "F": "f",
            "G": "g",
            "H": "h",
            "I": "i",
            "J": "j",
            "K": "k",
            "L": "l",
            "M": "m",
            "N": "n",
            "O": "o",
            "P": "p",
            "Q": "q",
            "R": "r",
            "S": "s",
            "T": "t",
            "U": "u",
            "V": "v",
            "W": "w",
            "X": "x",
            "Y": "y",
            "Z": "z"
          }
        const keys = document.getElementsByClassName("key");
        let res = [];
        let home = {};
        let fingers_present = {
            l_p : -1,
            l_m : -1,
            l_r : -1,
            l_i : -1,
            r_i : -1,
            r_m : -1,
            r_r : -1, 
            r_p: -1
        };
        let x = 0;
        for (let ky of keys) {
            if (!ky.classList.contains("keyword")) {
                if (!ky.hasAttribute("finger_res")) {
                    alert("Error: All keys must be mapped!");
                    return;
                }
                let finger = ky.getAttribute("finger_res");
                res.push(finger);
                if (fingers_present[finger] === -1) {
                    fingers_present[finger] = 0
                }
                if (ky.hasAttribute("finger_home")) {
                    home[finger] = x;
                    fingers_present[finger] = 1;
                }
                x += 1;
            }
        }
        for (const [key, value] of Object.entries(fingers_present)) {
            if(value === 0 && !(key in home)) {
                alert("Error: All fingers must have a home!");
                return;
            }
        }
        const json_obj = {
            "return_to_home": document.getElementById("return-preferance").value === "true",
            "alt_keys": alt_keys,
            "finger_duty": res,
            "original_finger_position": home
        }
        const json = JSON.stringify(json_obj);
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(json));
        element.setAttribute('download', 'my_config.json');
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    });
}