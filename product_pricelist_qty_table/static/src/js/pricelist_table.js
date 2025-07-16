
odoo.define('product_pricelist_qty_table.highlight_table', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.PricelistQtyTable = publicWidget.Widget.extend({
        selector: '.table-responsive',
        start: function () {
            this._attachEvents();
        },
        _attachEvents: function () {
            const rows = this.el.querySelectorAll('.hoverable-row');
            const qtyInput = document.querySelector('#quantity');
            if (!qtyInput) return;

            const highlightRow = (currentQty) => {
                let matched = null;
                rows.forEach(row => {
                    const minQty = parseFloat(row.dataset.qty);
                    row.classList.remove('selected-row');
                    if (currentQty >= minQty) {
                        matched = row;
                    }
                });
                if (matched) {
                    matched.classList.add('selected-row');
                }
            };

            rows.forEach(row => {
                row.addEventListener('click', () => {
                    const qty = parseFloat(row.dataset.qty);
                    qtyInput.value = qty;
                    qtyInput.dispatchEvent(new Event('input', { bubbles: true }));
                    qtyInput.dispatchEvent(new Event('change', { bubbles: true }));
                    highlightRow(qty);
                });
            });

            qtyInput.addEventListener('input', () => {
                const currentQty = parseFloat(qtyInput.value);
                if (!isNaN(currentQty)) {
                    highlightRow(currentQty);
                }
            });

            // Highlight on load
            const initialQty = parseFloat(qtyInput.value);
            if (!isNaN(initialQty)) {
                highlightRow(initialQty);
            }
        },
    });

    return publicWidget.registry.PricelistQtyTable;
});
