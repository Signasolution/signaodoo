/* ========================================
   AMÉLIORATION NAVIGATION - JAVASCRIPT SIMPLE
   ======================================== */

odoo.define('website_navigation_enhancement.navigation_simple', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var NavigationEnhancementSimple = publicWidget.Widget.extend({
        selector: 'body',
        events: {},

        /**
         * Initialisation du widget
         */
        start: function () {
            this._super.apply(this, arguments);
            this._initializeActiveStates();
            this._initializeHoverEffects();
        },

        /**
         * Initialise les états actifs des éléments de navigation
         */
        _initializeActiveStates: function () {
            var self = this;
            
            // Marquer l'élément de navigation actif
            this._markActiveNavigationItem();
            
            // Marquer la catégorie active
            this._markActiveCategory();
        },

        /**
         * Marque l'élément de navigation actif
         */
        _markActiveNavigationItem: function () {
            var currentPath = window.location.pathname;
            var currentPage = currentPath.split('/').pop();
            
            // Rechercher les liens de navigation
            this.$('a[href]').each(function () {
                var $link = $(this);
                var href = $link.attr('href');
                
                if (href && (currentPath.includes(href) || href.includes(currentPage))) {
                    $link.addClass('active');
                    $link.closest('li').addClass('active');
                }
            });
        },

        /**
         * Marque la catégorie active
         */
        _markActiveCategory: function () {
            var currentPath = window.location.pathname;
            var currentCategory = this._getCurrentCategoryFromPath(currentPath);
            
            if (currentCategory) {
                this.$('a[href]').each(function () {
                    var $link = $(this);
                    var linkText = $link.text().trim().toLowerCase();
                    var linkHref = $link.attr('href');
                    
                    if (linkText === currentCategory.toLowerCase() || 
                        (linkHref && currentPath.includes(linkHref))) {
                        $link.addClass('active');
                        $link.closest('li').addClass('active');
                    }
                });
            }
        },

        /**
         * Extrait la catégorie actuelle du chemin
         */
        _getCurrentCategoryFromPath: function (path) {
            // Logique pour extraire la catégorie du chemin
            var pathParts = path.split('/');
            var categoryIndex = pathParts.indexOf('shop') + 1;
            
            if (categoryIndex > 0 && pathParts[categoryIndex]) {
                return pathParts[categoryIndex].replace(/-/g, ' ');
            }
            
            return null;
        },

        /**
         * Initialise les effets de survol
         */
        _initializeHoverEffects: function () {
            var self = this;
            
            // Effet de survol pour les liens de navigation
            this.$('a[href]').hover(
                function () {
                    $(this).addClass('hover-effect');
                },
                function () {
                    $(this).removeClass('hover-effect');
                }
            );
        }
    });

    // Enregistrement du widget
    publicWidget.registry.websiteNavigationEnhancementSimple = NavigationEnhancementSimple;

    return {
        NavigationEnhancementSimple: NavigationEnhancementSimple
    };
});
