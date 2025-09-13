/** @odoo-module **/

// Système de fallback pour la compatibilité avec Odoo 18
(function() {
    'use strict';

    // Initialisation du tableau de prix dégressifs
    function initPriceBreakTables() {
        const widgets = document.querySelectorAll('.price-break-table-widget');
        widgets.forEach(widget => {
            if (!widget.dataset.initialized) {
                new PriceBreakTableWidget(widget);
                widget.dataset.initialized = 'true';
            }
        });
    }

    // Classe principale du widget
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
                
                if (result.result) {
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

    // Initialisation au chargement de la page
    document.addEventListener('DOMContentLoaded', initPriceBreakTables);
    
    // Réinitialisation après les mises à jour AJAX d'Odoo
    if (typeof odoo !== 'undefined') {
        odoo.define('price_break_table.auto_init', function (require) {
            const publicWidget = require('web.public.widget');
            
            publicWidget.registry.PriceBreakTableAutoInit = publicWidget.Widget.extend({
                selector: '.price-break-table-widget',
                start: function () {
                    initPriceBreakTables();
                    return this._super.apply(this, arguments);
                }
            });
        });
    }

    // Export pour compatibilité avec les modules OWL
    window.PriceBreakTableWidget = PriceBreakTableWidget;
    window.initPriceBreakTables = initPriceBreakTables;

})();