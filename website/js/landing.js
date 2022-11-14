
function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}

async function type(element) {
    let typeme = document.getElementById(element);
    typeme.style.opacity = "100%";
    const value = typeme.innerHTML;
    typeme.innerHTML = "";
    for (let char of value) {
        if (char === " ") {
            typeme.innerHTML += " ";
        }
        typeme.innerHTML += char;
        await delay(100);
    }
}

export async function initSite() {
    const sections = document.getElementsByClassName("hamburger-content");
    const active_height = 100 - (3 * (sections.length - 1)) - sections.length / 2;
    var animation_in_motion = false;
    document.documentElement.style.setProperty('--active-height', active_height.toString() + "vh");
    for (let section of sections) {
        if (!section.hasAttribute("active")) {
            section.style.height = "3vh";
        }
        section.addEventListener("click", async (e) => {
            if (section.hasAttribute("active") || animation_in_motion) {
                return;
            }
            animation_in_motion = true;
            let curr = document.querySelector("div[active]")
            curr.toggleAttribute("active");
            curr.toggleAttribute("inactive");
            if (section.hasAttribute("inactive")) {
                section.toggleAttribute('inactive');
            }
            section.toggleAttribute('active');
            await delay(1000);
            animation_in_motion = false;
        });
    }
    document.getElementById('landing-title').style.opacity = "0%";
    document.getElementById('landing-subtitle').style.opacity = "0%";
    await delay(1600);
    type('landing-title');
    await delay(2500);
    type('landing-subtitle');
}