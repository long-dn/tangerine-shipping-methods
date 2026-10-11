/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";
import websiteSaleAddress from "@website_sale/js/address";

/**
 * /shop/address: the wards of Vietnam belong to the states (2025 reform),
 * reload them each time the state changes.
 */
websiteSaleAddress.include({
    _getSelectedCountryCode() {
        const selectCountry = this.addressForm.country_id;
        const option = selectCountry && selectCountry.options[selectCountry.selectedIndex];
        return option ? option.getAttribute("code") : "";
    },

    _changeOption(selectElement, choices, defaultValue) {
        // empty existing options, only keep the placeholder.
        selectElement.options.length = 1;
        choices.forEach((item) => {
            const option = new Option(item[1], item[0]);
            option.setAttribute("data-code", item[2]);
            if (defaultValue && item[0] == defaultValue) {
                option.selected = true;
            }
            selectElement.appendChild(option);
        });
    },

    async _changeCountry(init = false) {
        await this._super(...arguments);
        if (!this.addressForm.ward_id) {
            return;
        }
        if (this._getSelectedCountryCode() !== "VN") {
            this._changeOption(this.addressForm.ward_id, []);
            this._hideInput("ward_id");
        } else if (!init) {
            // the states have been reloaded, so are the wards
            await this._changeStateVN();
        }
    },

    async _onChangeState(ev) {
        await this._super(...arguments);
        if (this.addressForm.ward_id && this._getSelectedCountryCode() === "VN") {
            await this._changeStateVN();
        }
    },

    async _changeStateVN() {
        const selectWards = this.addressForm.ward_id;
        const stateId = parseInt(this.addressForm.state_id.value);
        let choices = [];
        if (stateId) {
            const data = await rpc(`/my/address/state_vn_info/${stateId}`);
            choices = data.wards;
        }
        this._changeOption(selectWards, choices, selectWards.value);
        if (choices.length) {
            this._showInput("ward_id");
        } else {
            this._hideInput("ward_id");
        }
    },
});
