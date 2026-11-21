(function () {
    "use strict";

    function bind(field) {
        const form = field.closest("form");
        const country = form.elements.country_id;
        const state = form.elements.state_id;
        const ward = form.elements.ward_id;
        let revision = 0;
        async function update(selected) {
            const current = ++revision;
            const isVietnam = country.value === field.dataset.country;
            field.hidden = !isVietnam;
            ward.required = isVietnam;
            ward.options.length = 1;
            ward.value = "";
            if (!isVietnam || !state.value) {
                return;
            }
            const stateId = state.value;
            const response = await fetch("/shop/vietnam/wards/" + encodeURIComponent(stateId));
            if (!response.ok) {
                throw new Error("Could not load wards");
            }
            const choices = await response.json();
            if (current !== revision || state.value !== stateId || country.value !== field.dataset.country) {
                return;
            }
            for (const [id, name] of choices) {
                ward.add(new Option(name, id, false, String(id) === selected));
            }
        }
        state.addEventListener("change", () => update(""));
        country.addEventListener("change", () => update(""));
        update(field.dataset.selected);
    }
    function start() {
        document.querySelectorAll("[data-vietnam-ward]").forEach(bind);
    }
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();
