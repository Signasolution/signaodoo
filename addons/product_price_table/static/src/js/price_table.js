odoo.define('product_price_table.price_table', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.PriceTable = publicWidget.Widget.extend({
        selector: '#price-break-table',
        events: {
            'mouseover .price-row': '_onHoverRow',
            'mouseout .price-row': '_onLeaveRow',
            'click .price-row': '_onClickRow',
        },

        _onHoverRow: function (ev) {
            ev.currentTarget.classList.add('table-active');
        },

        _onLeaveRow: function (ev) {
            ev.currentTarget.classList.remove('table-active');
        },

        _onClickRow: function (ev) {
            const qty = ev.currentTarget.dataset.qty;
            const input = document.querySelector('#add_to_cart input[name="add_qty"]');
            if (input && qty) {
                input.value = qty;
                input.dispatchEvent(new Event('change'));
            }
        }
    });
});