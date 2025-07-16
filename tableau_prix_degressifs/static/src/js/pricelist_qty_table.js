odoo.define('product_pricelist_qty_table.frontend', function (require) {
    const publicWidget = require('web.public.widget');
    publicWidget.registry.PricelistQtyTable = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        events: {
            'click .pricelist-row': '_onRowClick',
            'change input[name="add_qty"]': '_onQtyChange',
        },

        _onRowClick: function (ev) {
            const $row = $(ev.currentTarget);
            const qty = parseFloat($row.data('quantity'));
            $('input[name="add_qty"]').val(qty).trigger('change');
        },

        _onQtyChange: function (ev) {
            const qty = parseFloat($(ev.currentTarget).val());
            $('.pricelist-row').removeClass('selected-row');
            $('.pricelist-row').each(function () {
                const $r = $(this);
                if (qty >= parseFloat($r.data('quantity'))) {
                    $r.addClass('selected-row');
                }
            });
        }
    });
    return publicWidget.registry.PricelistQtyTable;
});
