/** Ajoute les classes CSS selon la hiérarchie et l’état actif dans le menu des catégories produits sur le site */
odoo.define('product_category_ui_enhancer.category_ui', function (require) {
    'use strict';

    $(document).ready(function () {
        // Cible le menu des catégories dans le shop (standard Odoo)
        $('.o_wsale_products_categories ul > li').each(function () {
            var $li = $(this);
            var level = 1 + $li.parents('ul').length - 1; // profondeur hiérarchique

            $li.addClass('pcui-item').addClass('pcui-level-' + level);

            // Ajoute l'icône ▲ sur les catégories principales
            if (level === 1) {
                $li.find('a').first().addClass('pcui-main-icon');
            }

            // Surbrillance si actif
            if ($li.hasClass('active')) {
                $li.addClass('pcui-active');
            }
        });
    });
});
