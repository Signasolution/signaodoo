/** @odoo-module **/

// Initialisation automatique du tableau de prix dégressifs
(function() {
    'use strict';

    // Fonction pour initialiser automatiquement les tableaux de prix
    function autoInitPriceBreakTables() {
        // Attendre que la page soit complètement chargée
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initTables);
        } else {
            initTables();
        }
    }

    function initTables() {
        // Initialiser les tableaux existants
        const widgets = document.querySelectorAll('.price-break-table-widget');
        widgets.forEach(widget => {
            if (!widget.dataset.initialized) {
                new PriceBreakTableWidget(widget);
                widget.dataset.initialized = 'true';
            }
        });

        // Ajouter des tableaux aux pages produits si nécessaire
        addTablesToProductPages();
    }

    function addTablesToProductPages() {
        // Ajouter le tableau aux pages produits qui n'en ont pas
        const productPages = document.querySelectorAll('.oe_website_sale, .o_form_view');
        productPages.forEach(page => {
            if (!page.querySelector('.price-break-table-widget')) {
                const productId = getProductIdFromPage(page);
                if (productId) {
                    addPriceBreakTable(page, productId);
                }
            }
        });
    }

    function getProductIdFromPage(page) {
        // Essayer différentes méthodes pour obtenir l'ID du produit
        let productId = null;

        // Méthode 1: Input hidden
        const productInput = page.querySelector('input[name="product_template_id"]');
        if (productInput) {
            productId = productInput.value;
        }

        // Méthode 2: Meta tag
        if (!productId) {
            const metaTag = page.querySelector('meta[name="product-id"]');
            if (metaTag) {
                productId = metaTag.content;
            }
        }

        // Méthode 3: URL
        if (!productId) {
            const urlMatch = window.location.pathname.match(/\/product\/(\d+)/);
            if (urlMatch) {
                productId = urlMatch[1];
            }
        }

        // Méthode 4: Data attributes
        if (!productId) {
            const productElement = page.querySelector('[data-product-id]');
            if (productElement) {
                productId = productElement.dataset.productId;
            }
        }

        return productId;
    }

    function addPriceBreakTable(container, productId) {
        // Créer le widget de tableau de prix
        const widget = document.createElement('div');
        widget.className = 'price-break-table-widget';
        widget.dataset.productId = productId;
        widget.dataset.pricelistId = getPricelistId();
        widget.dataset.partnerId = getPartnerId();
        widget.dataset.currentQuantity = getCurrentQuantity();

        // Ajouter le widget au conteneur approprié
        const targetContainer = findTargetContainer(container);
        if (targetContainer) {
            targetContainer.appendChild(widget);
            new PriceBreakTableWidget(widget);
        }
    }

    function findTargetContainer(page) {
        // Chercher un conteneur approprié pour ajouter le tableau
        const selectors = [
            '.product_price',
            '.oe_product_price',
            '.price',
            '.product_details',
            '.o_field_price',
            '.o_field_monetary[name="list_price"]'
        ];

        for (const selector of selectors) {
            const element = page.querySelector(selector);
            if (element) {
                // Créer un conteneur parent
                const container = document.createElement('div');
                container.className = 'price-break-container';
                container.style.marginTop = '15px';
                
                // Insérer après l'élément trouvé
                element.parentNode.insertBefore(container, element.nextSibling);
                return container;
            }
        }

        // Fallback: ajouter à la fin de la page
        return page;
    }

    function getPricelistId() {
        const pricelistInput = document.querySelector('input[name="pricelist_id"]');
        return pricelistInput ? pricelistInput.value : '1';
    }

    function getPartnerId() {
        const partnerInput = document.querySelector('input[name="partner_id"]');
        return partnerInput ? partnerInput.value : null;
    }

    function getCurrentQuantity() {
        const quantityInput = document.querySelector('input[name="add_qty"], input[name="quantity"], input[name="product_uom_qty"]');
        return quantityInput ? quantityInput.value : '1';
    }

    // Classe principale du widget (réutilisée depuis le fichier principal)
    class PriceBreakTableWidget {
        constructor(element) {
            this.element = element;
            this.productId = this.getDataAttribute('product-id');
            this.pricelistId = this.getDataAttribute('pricelist-id');
            this.partnerId = this.getDataAttribute('partner-id');
            this.currentQuantity = parseFloat(this.getDataAttribute('current-quantity')) || 1;
            
            if (!this.productId) {
                console.warn('Price Break Table: Product ID not found');
                return;
            }
            
            this.init();
        }

        getDataAttribute(name) {
            const value = this.element.dataset[name];
            return value && value !== 'undefined' ? value : null;
        }

        async init() {
            this.showLoading();
            await this.loadTableData();
            this.setupEventListeners();
        }

        async loadTableData(quantity = null) {
            if (!this.productId) return;
            
            const qty = quantity || this.currentQuantity;
            
            try {
                const response = await fetch('/web/dataset/call_kw', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {
                            model: 'product.template',
                            method: 'get_price_break_table_js_data',
                            args: [parseInt(this.productId)],
                            kwargs: {
                                pricelist_id: this.pricelistId ? parseInt(this.pricelistId) : null,
                                partner_id: this.partnerId ? parseInt(this.partnerId) : null,
                                quantity: qty,
                            }
                        },
                        id: Math.floor(Math.random() * 1000000)
                    })
                });
                
                const result = await response.json();
                
                if (result.result && result.result.rows && result.result.rows.length > 0) {
                    this.renderTable(result.result);
                    this.currentQuantity = qty;
                } else {
                    this.renderEmpty();
                }
                
            } catch (error) {
                console.error('Erreur lors du chargement du tableau de prix:', error);
                this.renderError();
            }
        }

        setupEventListeners() {
            // Écoute des changements de quantité
            const quantityInputs = document.querySelectorAll('input[name="add_qty"], input[name="quantity"], input[name="product_uom_qty"]');
            quantityInputs.forEach(input => {
                input.addEventListener('input', (e) => this.onQuantityChange(e));
                input.addEventListener('change', (e) => this.onQuantityChange(e));
            });
        }

        onQuantityChange(event) {
            const newQuantity = parseFloat(event.target.value) || 1;
            if (Math.abs(newQuantity - this.currentQuantity) > 0.01) {
                this.loadTableData(newQuantity);
            }
        }

        onRowClick(row) {
            if (!row.min_quantity) return;
            
            // Mise à jour de la quantité dans l'input
            const quantityInput = document.querySelector('input[name="add_qty"], input[name="quantity"], input[name="product_uom_qty"]');
            if (quantityInput) {
                quantityInput.value = row.min_quantity;
                quantityInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
            
            // Mise à jour de l'affichage
            this.loadTableData(row.min_quantity);
        }

        showLoading() {
            this.element.innerHTML = `
                <div class="price-break-table-loading">
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Chargement...</span>
                    </div>
                    <span class="ms-2">Chargement des prix...</span>
                </div>
            `;
        }

        renderTable(data) {
            if (!data.rows || data.rows.length === 0) {
                this.renderEmpty();
                return;
            }

            const rowsHtml = data.rows.map(row => this.renderTableRow(row)).join('');
            
            this.element.innerHTML = `
                <div class="price-break-table-container">
                    <h6 class="price-break-table-title">
                        <i class="fa fa-table me-2"></i>
                        Prix dégressifs par quantité
                    </h6>
                    <div class="table-responsive">
                        <table class="table table-sm table-hover price-break-table">
                            <thead class="table-light">
                                <tr>
                                    <th>Quantité</th>
                                    <th class="text-end">Prix unitaire</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rowsHtml}
                            </tbody>
                        </table>
                    </div>
                    <small class="text-muted">
                        <i class="fa fa-info-circle me-1"></i>
                        Cliquez sur une ligne pour ajuster la quantité
                    </small>
                </div>
            `;

            // Ajout des event listeners aux lignes
            const rows = this.element.querySelectorAll('.price-break-clickable');
            rows.forEach((row, index) => {
                row.addEventListener('click', () => this.onRowClick(data.rows[index]));
            });
        }

        renderTableRow(row) {
            const activeClass = row.is_active ? 'price-break-active' : '';
            const clickableClass = 'price-break-clickable';
            
            return `
                <tr class="${activeClass} ${clickableClass}" 
                    data-min-qty="${row.min_quantity}" 
                    data-max-qty="${row.max_quantity || ''}">
                    <td>
                        <strong>${row.quantity_display}</strong>
                        ${row.is_active ? '<i class="fa fa-check-circle text-success ms-2"></i>' : ''}
                    </td>
                    <td class="text-end">
                        <strong>${row.price_formatted}</strong>
                    </td>
                </tr>
            `;
        }

        renderEmpty() {
            this.element.innerHTML = `
                <div class="price-break-table-empty">
                    <p class="text-muted mb-0">Aucun prix dégressif disponible pour ce produit.</p>
                </div>
            `;
        }

        renderError() {
            this.element.innerHTML = `
                <div class="price-break-table-empty">
                    <p class="text-danger mb-0">Erreur lors du chargement des prix dégressifs.</p>
                </div>
            `;
        }
    }

    // Initialisation automatique
    autoInitPriceBreakTables();

    // Réinitialisation après les mises à jour AJAX
    if (typeof odoo !== 'undefined') {
        odoo.define('price_break_table.auto_init', function (require) {
            const publicWidget = require('web.public.widget');
            
            publicWidget.registry.PriceBreakTableAutoInit = publicWidget.Widget.extend({
                selector: 'body',
                start: function () {
                    setTimeout(initTables, 1000);
                    return this._super.apply(this, arguments);
                }
            });
        });
    }

    // Export global
    window.PriceBreakTableWidget = PriceBreakTableWidget;
    window.autoInitPriceBreakTables = autoInitPriceBreakTables;

})();
