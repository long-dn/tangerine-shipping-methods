/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";
import portalDetails from "@portal/js/portal";

/**
 * /my/account: the wards of Vietnam belong to the states (2025 reform),
 * reload them each time the state changes.
 */
portalDetails.include({
    events: Object.assign({}, portalDetails.prototype.events, {
        'change select[name="state_id"]': "_onStateChangeVN",
    }),

    /**
     * @override
     */
    start: function () {
        // _adaptAddressForm is called by the super start
        this.$ward = this.$('select[name="ward_id"]');
        return this._super.apply(this, arguments);
    },

    _isVietnamSelected: function () {
        const vnCountryId = this.$ward.attr("data-vn_country_id");
        const countryId = this.$('select[name="country_id"]').val();
        return Boolean(vnCountryId) && vnCountryId === countryId;
    },

    _setWardOptions: function (wards) {
        const selectWards = this.$ward[0];
        const currentWardId = selectWards.value;
        // empty existing options, only keep the placeholder.
        selectWards.options.length = 1;
        wards.forEach((ward) => {
            const option = new Option(ward[1], ward[0]);
            option.setAttribute("data-code", ward[2]);
            if (currentWardId && ward[0] == currentWardId) {
                option.selected = true;
            }
            selectWards.appendChild(option);
        });
        this.$ward.parent().toggle(wards.length >= 1);
    },

    _loadWardsVN: async function () {
        const stateId = parseInt(this.$state.val());
        let wards = [];
        if (stateId) {
            const data = await rpc(`/my/address/state_vn_info/${stateId}`);
            wards = data.wards;
        }
        this._setWardOptions(wards);
    },

    /**
     * @override
     */
    _adaptAddressForm: function () {
        this._super.apply(this, arguments);
        if (this.$ward && this.$ward.length && !this._isVietnamSelected()) {
            this._setWardOptions([]);
        }
    },

    /**
     * @override
     */
    _onCountryChange: function () {
        this._super.apply(this, arguments);
        if (this.$ward.length && this._isVietnamSelected()) {
            return this._loadWardsVN();
        }
    },

    _onStateChangeVN: function () {
        if (this.$ward.length && this._isVietnamSelected()) {
            return this._loadWardsVN();
        }
    },
});
