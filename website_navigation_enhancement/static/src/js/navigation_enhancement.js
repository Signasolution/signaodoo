/* ========================================
   AMÉLIORATION NAVIGATION - JAVASCRIPT
   ======================================== */

odoo.define('website_navigation_enhancement.navigation', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');

    var NavigationEnhancement = publicWidget.Widget.extend({
        selector: '.website-navigation, .category-menu',
        events: {
            'click .category-title': '_onToggleCategoryMenu',
            'click .nav-link': '_onNavLinkClick',
            'click .category-link': '_onCategoryLinkClick',
        },

        /**
         * Initialisation du widget
         */
        start: function () {
            this._super.apply(this, arguments);
            this._initializeActiveStates();
            this._initializeBreadcrumbs();
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
            this.$('.nav-link').each(function () {
                var $link = $(this);
                var href = $link.attr('href');
                
                if (href && (currentPath.includes(href) || href.includes(currentPage))) {
                    $link.closest('.nav-item').addClass('active');
                    $link.addClass('active');
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
                this.$('.category-link').each(function () {
                    var $link = $(this);
                    var linkText = $link.text().trim().toLowerCase();
                    var linkHref = $link.attr('href');
                    
                    if (linkText === currentCategory.toLowerCase() || 
                        (linkHref && currentPath.includes(linkHref))) {
                        $link.closest('.category-item').addClass('active');
                        $link.addClass('active');
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
         * Initialise le fil d'Ariane
         */
        _initializeBreadcrumbs: function () {
            var breadcrumbData = this._generateBreadcrumbData();
            if (breadcrumbData.length > 1) {
                this._renderBreadcrumb(breadcrumbData);
            }
        },

        /**
         * Génère les données du fil d'Ariane
         */
        _generateBreadcrumbData: function () {
            var breadcrumbs = [];
            var currentPath = window.location.pathname;
            var pathParts = currentPath.split('/').filter(function(part) {
                return part && part !== 'shop' && part !== 'product';
            });
            
            // Ajouter l'accueil
            breadcrumbs.push({
                name: 'Accueil',
                url: '/',
                active: false
            });
            
            // Ajouter les catégories
            var currentUrl = '/';
            pathParts.forEach(function(part, index) {
                currentUrl += part + '/';
                var isLast = index === pathParts.length - 1;
                
                breadcrumbs.push({
                    name: part.replace(/-/g, ' ').replace(/\b\w/g, function(l) {
                        return l.toUpperCase();
                    }),
                    url: currentUrl,
                    active: isLast
                });
            });
            
            return breadcrumbs;
        },

        /**
         * Affiche le fil d'Ariane
         */
        _renderBreadcrumb: function (breadcrumbData) {
            var $breadcrumb = $('<div class="website-breadcrumb"><nav aria-label="breadcrumb"><ol class="breadcrumb"></ol></nav></div>');
            var $breadcrumbList = $breadcrumb.find('.breadcrumb');
            
            breadcrumbData.forEach(function(item) {
                var $breadcrumbItem = $('<li class="breadcrumb-item"></li>');
                
                if (item.active) {
                    $breadcrumbItem.addClass('active').text(item.name);
                } else {
                    $breadcrumbItem.append($('<a href="' + item.url + '">' + item.name + '</a>'));
                }
                
                $breadcrumbList.append($breadcrumbItem);
            });
            
            // Insérer le fil d'Ariane au début du contenu principal
            var $mainContent = $('.oe_website_sale, .container, main').first();
            if ($mainContent.length) {
                $mainContent.prepend($breadcrumb);
            }
        },

        /**
         * Initialise les effets de survol
         */
        _initializeHoverEffects: function () {
            var self = this;
            
            // Effet de survol pour les liens de navigation
            this.$('.nav-link').hover(
                function () {
                    $(this).addClass('hover-effect');
                },
                function () {
                    $(this).removeClass('hover-effect');
                }
            );
            
            // Effet de survol pour les liens de catégories
            this.$('.category-link').hover(
                function () {
                    $(this).addClass('hover-effect');
                },
                function () {
                    $(this).removeClass('hover-effect');
                }
            );
        },

        /**
         * Gestion du clic sur le titre de catégorie (toggle)
         */
        _onToggleCategoryMenu: function (ev) {
            ev.preventDefault();
            var $title = $(ev.currentTarget);
            var $menu = $title.siblings('.category-list');
            
            $title.toggleClass('collapsed');
            $menu.slideToggle(300);
        },

        /**
         * Gestion du clic sur les liens de navigation
         */
        _onNavLinkClick: function (ev) {
            var $link = $(ev.currentTarget);
            var href = $link.attr('href');
            
            if (href && !href.startsWith('#')) {
                // Ajouter un effet de chargement
                this._showLoadingEffect($link);
            }
        },

        /**
         * Gestion du clic sur les liens de catégories
         */
        _onCategoryLinkClick: function (ev) {
            var $link = $(ev.currentTarget);
            var href = $link.attr('href');
            
            if (href && !href.startsWith('#')) {
                // Marquer comme actif
                this.$('.category-item').removeClass('active');
                $link.closest('.category-item').addClass('active');
                
                // Ajouter un effet de chargement
                this._showLoadingEffect($link);
            }
        },

        /**
         * Affiche un effet de chargement
         */
        _showLoadingEffect: function ($element) {
            var originalText = $element.text();
            $element.addClass('loading');
            
            // Simuler un effet de chargement
            setTimeout(function () {
                $element.removeClass('loading');
            }, 500);
        },

        /**
         * Met à jour la position actuelle
         */
        updateCurrentPosition: function (categoryName) {
            // Mettre à jour le fil d'Ariane
            this._initializeBreadcrumbs();
            
            // Mettre à jour les états actifs
            this._initializeActiveStates();
        }
    });

    // Widget pour le fil d'Ariane autonome
    var BreadcrumbWidget = publicWidget.Widget.extend({
        selector: 'body',
        events: {},

        start: function () {
            this._super.apply(this, arguments);
            this._initializeBreadcrumb();
        },

        _initializeBreadcrumb: function () {
            var breadcrumbData = this._generateBreadcrumbData();
            if (breadcrumbData.length > 1) {
                this._renderBreadcrumb(breadcrumbData);
            }
        },

        _generateBreadcrumbData: function () {
            var breadcrumbs = [];
            var currentPath = window.location.pathname;
            var pathParts = currentPath.split('/').filter(function(part) {
                return part && part !== 'shop' && part !== 'product';
            });
            
            // Ajouter l'accueil
            breadcrumbs.push({
                name: 'Accueil',
                url: '/',
                active: false
            });
            
            // Ajouter les catégories
            var currentUrl = '/';
            pathParts.forEach(function(part, index) {
                currentUrl += part + '/';
                var isLast = index === pathParts.length - 1;
                
                breadcrumbs.push({
                    name: part.replace(/-/g, ' ').replace(/\b\w/g, function(l) {
                        return l.toUpperCase();
                    }),
                    url: currentUrl,
                    active: isLast
                });
            });
            
            return breadcrumbs;
        },

        _renderBreadcrumb: function (breadcrumbData) {
            var $breadcrumb = $('<div class="website-breadcrumb"><nav aria-label="breadcrumb"><ol class="breadcrumb"></ol></nav></div>');
            var $breadcrumbList = $breadcrumb.find('.breadcrumb');
            
            breadcrumbData.forEach(function(item) {
                var $breadcrumbItem = $('<li class="breadcrumb-item"></li>');
                
                if (item.active) {
                    $breadcrumbItem.addClass('active').text(item.name);
                } else {
                    $breadcrumbItem.append($('<a href="' + item.url + '">' + item.name + '</a>'));
                }
                
                $breadcrumbList.append($breadcrumbItem);
            });
            
            // Insérer le fil d'Ariane au début du contenu principal
            var $mainContent = $('.oe_website_sale, .container, main').first();
            if ($mainContent.length) {
                $mainContent.prepend($breadcrumb);
            }
        }
    });

    // Enregistrement des widgets
    publicWidget.registry.websiteNavigationEnhancement = NavigationEnhancement;
    publicWidget.registry.websiteBreadcrumb = BreadcrumbWidget;

    return {
        NavigationEnhancement: NavigationEnhancement,
        BreadcrumbWidget: BreadcrumbWidget
    };
});
