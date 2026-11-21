import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { CustomerAddress } from "@portal/interactions/address";

patch(CustomerAddress.prototype, {
    async onChangeCountry() {
        const data = await super.onChangeCountry(...arguments);
        await this._updateVietnamWards();
        return data;
    },

    async onChangeState() {
        const data = await super.onChangeState(...arguments);
        await this._updateVietnamWards();
        return data;
    },

    /**
     * Wards of Vietnam belong to a state: reload them when the state changes.
     */
    async _updateVietnamWards() {
        if (!this.addressForm.ward_id) {
            return;
        }
        const stateId = parseInt(this.addressForm.state_id.value);
        const selected = this.addressForm.ward_id.value;
        let wards = [];
        if (this._getSelectedCountryCode() === "VN" && stateId) {
            const data = await this.waitFor(rpc(`/my/address/state_vn_info/${stateId}`, {}));
            if (parseInt(this.addressForm.state_id.value) !== stateId || this._getSelectedCountryCode() !== "VN") return;
            wards = data.wards;
        }
        this._setFieldChoices("ward_id", wards);
        this.addressForm.ward_id.disabled = !wards.length;
        if (wards.some((ward) => String(ward.id) === selected)) {
            this.addressForm.ward_id.value = selected;
        }
    },
});
