/** @odoo-module **/

// Système ultra-simple pour l'affichage des prix dégressifs
(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        debug: false,
        autoInit: true,
        checkInterval: 2000,
        maxRetries: 10
    };

    let initialized = false;
    let retryCount = 0;

    // Fonction de log pour le debug
    function log(message, ...args) {
        if (CONFIG.debug) {
            console.log('[PriceBreak]', message, ...args);
        }
    }

    // Fonction principale d'initialisation
    function init() {
        if (initialized) return;
        
        log('Initialisation du système de prix dégressifs...');
        
        // Attendre que la page soit prête
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', startInitialization);
        } else {
            startInitialization();
        }
    }

    function startInitialization() {
        // Vérifier périodiquement s'il y a des pages produits à traiter
        const interval = setInterval(() => {
            if (processProductPages()) {
                clearInterval(interval);
                initialized = true;
                log('Initialisation terminée');
            } else if (retryCount >= CONFIG.maxRetries) {
                clearInterval(interval);
                log('Nombre maximum de tentatives atteint');
            }
            retryCount++;
        }, CONFIG.checkInterval);
    }

    function processProductPages() {
        let foundProducts = false;

        // Chercher les pages produits
        const productSelectors = [
            '.oe_website_sale',
            '.product_detail',
            '.product_info',
            '[data-product-template-id]',
            '.js_product'
        ];

        for (const selector of productSelectors) {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (processProductElement(element)) {
                    foundProducts = true;
                }
            });
        }

        return foundProducts;
    }

    function processProductElement(element) {
        // Vérifier si déjà traité
        if (element.dataset.priceBreakProcessed) {
            return false;
        }

        const productId = getProductId(element);
        if (!productId) {
            log('ID produit non trouvé pour l\'élément:', element);
            return false;
        }

        log('Traitement du produit ID:', productId);

        // Marquer comme traité
        element.dataset.priceBreakProcessed = 'true';

        // Ajouter le tableau de prix
        addPriceBreakTable(element, productId);

        return true;
    }

    function getProductId(element) {
        // Méthode 1: Data attribute direct
        let productId = element.dataset.productTemplateId || element.dataset.productId;
        if (productId) return productId;

        // Méthode 2: Input hidden
        const productInput = element.querySelector('input[name="product_template_id"]');
        if (productInput) return productInput.value;

        // Méthode 3: Meta tag
        const metaTag = element.querySelector('meta[name="product-id"]');
        if (metaTag) return metaTag.content;

        // Méthode 4: URL
        const urlMatch = window.location.pathname.match(/\/product\/(\d+)/);
        if (urlMatch) return urlMatch[1];

        // Méthode 5: Recherche dans le contexte parent
        const parentElement = element.closest('body');
        if (parentElement) {
            const globalProductInput = parentElement.querySelector('input[name="product_template_id"]');
            if (globalProductInput) return globalProductInput.value;
        }

        return null;
    }

    function addPriceBreakTable(container, productId) {
        // Créer le conteneur du tableau
        const tableContainer = document.createElement('div');
        tableContainer.className = 'price-break-table-widget';
        tableContainer.dataset.productId = productId;
        tableContainer.dataset.pricelistId = getPricelistId();
        tableContainer.dataset.partnerId = getPartnerId();
        tableContainer.dataset.currentQuantity = getCurrentQuantity();
        tableContainer.style.marginTop = '20px';

        // Trouver l'emplacement approprié
        const targetLocation = findTargetLocation(container);
        if (targetLocation) {
            targetLocation.appendChild(tableContainer);
            
            // Initialiser le widget
            new SimplePriceBreakWidget(tableContainer);
            log('Tableau de prix ajouté pour le produit:', productId);
        } else {
            log('Emplacement non trouvé pour le produit:', productId);
        }
    }

    function findTargetLocation(container) {
        // Sélecteurs pour trouver l'emplacement approprié
        const selectors = [
            '.product_price',
            '.oe_product_price',
            '.price',
            '.product_details',
            '.product_info',
            '.product_extra_info',
            '.js_product',
            '.product_detail'
        ];

        for (const selector of selectors) {
            const element = container.querySelector(selector);
            if (element) {
                // Créer un conteneur parent
                const wrapper = document.createElement('div');
                wrapper.className = 'price-break-wrapper';
                wrapper.style.marginTop = '15px';
                
                // Insérer après l'élément trouvé
                element.parentNode.insertBefore(wrapper, element.nextSibling);
                return wrapper;
            }
        }

        // Fallback: ajouter à la fin du conteneur
        return container;
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

    // Widget simple pour le tableau de prix
    class SimplePriceBreakWidget {
        constructor(element) {
            this.element = element;
            this.productId = element.dataset.productId;
            this.pricelistId = element.dataset.pricelistId;
            this.partnerId = element.dataset.partnerId;
            this.currentQuantity = parseFloat(element.dataset.currentQuantity) || 1;
            
            this.init();
        }

        async init() {
            this.showLoading();
            await this.loadData();
            this.setupListeners();
        }

        async loadData(quantity = null) {
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
                log('Erreur lors du chargement:', error);
                this.renderError();
            }
        }

        setupListeners() {
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
                this.loadData(newQuantity);
            }
        }

        onRowClick(row) {
            if (!row.min_quantity) return;
            
            // Mise à jour de la quantité
            const quantityInput = document.querySelector('input[name="add_qty"], input[name="quantity"], input[name="product_uom_qty"]');
            if (quantityInput) {
                quantityInput.value = row.min_quantity;
                quantityInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
            
            this.loadData(row.min_quantity);
        }

        showLoading() {
            this.element.innerHTML = `
                <div class="price-break-loading" style="text-align: center; padding: 10px;">
                    <small>Chargement des prix dégressifs...</small>
                </div>
            `;
        }

        renderTable(data) {
            const rowsHtml = data.rows.map(row => `
                <tr class="price-break-row ${row.is_active ? 'active' : ''}" 
                    data-min-qty="${row.min_quantity}" 
                    style="cursor: pointer; ${row.is_active ? 'background-color: #e8f5e8;' : ''}"
                    onclick="this.onRowClick(${JSON.stringify(row).replace(/"/g, '&quot;')})">
                    <td><strong>${row.quantity_display}</strong></td>
                    <td style="text-align: right;"><strong>${row.price_formatted}</strong></td>
                </tr>
            `).join('');
            
            this.element.innerHTML = `
                <div class="price-break-container" style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; background: #f9f9f9; margin: 10px 0;">
                    <h6 style="margin-bottom: 10px; color: #333;">
                        📊 Prix dégressifs par quantité
                    </h6>
                    <table class="table table-sm" style="margin-bottom: 10px; font-size: 0.9em;">
                        <thead style="background-color: #f5f5f5;">
                            <tr>
                                <th>Quantité</th>
                                <th style="text-align: right;">Prix unitaire</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHtml}
                        </tbody>
                    </table>
                    <small style="color: #666;">
                        💡 Cliquez sur une ligne pour ajuster la quantité
                    </small>
                </div>
            `;

            // Ajouter les event listeners
            const rows = this.element.querySelectorAll('.price-break-row');
            rows.forEach((row, index) => {
                row.addEventListener('click', () => this.onRowClick(data.rows[index]));
            });
        }

        renderEmpty() {
            this.element.innerHTML = `
                <div class="price-break-empty" style="text-align: center; padding: 10px; color: #666;">
                    <small>Aucun prix dégressif disponible pour ce produit.</small>
                </div>
            `;
        }

        renderError() {
            this.element.innerHTML = `
                <div class="price-break-error" style="text-align: center; padding: 10px; color: #d32f2f;">
                    <small>Erreur lors du chargement des prix dégressifs.</small>
                </div>
            `;
        }
    }

    // Initialisation automatique
    if (CONFIG.autoInit) {
        init();
    }

    // Export global pour debug
    window.PriceBreakSimple = {
        init: init,
        config: CONFIG,
        widget: SimplePriceBreakWidget
    };

})();
