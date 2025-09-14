// Tableau de prix dégressifs pour Odoo - Version unifiée
// Toutes les fonctionnalités dans un seul fichier

// Fonction pour vérifier si on est sur une page produit du site web
function isProductPage() {
    // 1. Vérifier qu'on est sur le site web (pas le backend)
    if (document.querySelector('.o_web_client')) {
        return false; // Backend Odoo
    }
    
    // 2. Détection positive : chercher les combinaisons d'éléments qui définissent une page produit
    
    // Combinaison 1: Champ quantité + Bouton ajouter au panier + Prix produit
    const hasQuantityField = document.querySelector('input[name="add_qty"]') !== null;
    const hasAddButton = document.querySelector('button[name="add"]') !== null;
    const hasProductPrice = document.querySelector('.product_price, .oe_product_price, .product_price_text') !== null;
    
    if (hasQuantityField && hasAddButton && hasProductPrice) {
        return true;
    }
    
    // Combinaison 2: Élément .js_product + données produit template
    const hasJsProduct = document.querySelector('.js_product') !== null;
    const hasProductTemplateId = document.querySelector('[data-product-template-id]') !== null;
    
    if (hasJsProduct && hasProductTemplateId) {
        return true;
    }
    
    // Combinaison 3: Détail produit + sélecteur de variantes
    const hasProductDetail = document.querySelector('.product_detail, #product_detail') !== null;
    const hasVariantSelector = document.querySelector('.js_add_cart_variant, .product_template_selector') !== null;
    
    if (hasProductDetail && hasVariantSelector) {
        return true;
    }
    
    // Combinaison 4: Produit principal + champ quantité
    const hasMainProduct = document.querySelector('.js_main_product') !== null;
    
    if (hasMainProduct && hasQuantityField) {
        return true;
    }
    
    // Combinaison 5: Vérifier qu'on a un seul produit affiché (pas une liste)
    const productCount = document.querySelectorAll('.js_product, .product_detail').length;
    const hasSingleProduct = productCount === 1;
    
    if (hasSingleProduct && (hasQuantityField || hasProductPrice)) {
        return true;
    }
    
    return false;
}

// Fonction principale
function initPriceBreak() {
    if (!isProductPage()) {
        return;
    }
    
    const productSelectors = [
        '.oe_website_sale',
        '.product_detail',
        '.product_info',
        '[data-product-template-id]',
        '.js_product',
        '.product'
    ];
    
    let foundProducts = false;
    
    for (const selector of productSelectors) {
        const elements = document.querySelectorAll(selector);
        
        elements.forEach(element => {
            if (processProductElement(element)) {
                foundProducts = true;
            }
        });
    }
    
    if (!foundProducts) {
        setTimeout(initPriceBreak, 2000);
    }
}

// Variable globale pour éviter les doublons
window.priceBreakProcessed = window.priceBreakProcessed || new Set();

function processProductElement(element) {
    if (element.dataset.priceBreakProcessed) {
        return false;
    }
    
    // Vérifier que l'élément contient une combinaison spécifique de page produit
    const hasQuantityField = element.querySelector('input[name="add_qty"]') !== null;
    const hasAddButton = element.querySelector('button[name="add"]') !== null;
    const hasProductPrice = element.querySelector('.product_price, .oe_product_price, .product_price_text') !== null;
    const hasJsProduct = element.querySelector('.js_product') !== null;
    const hasProductTemplateId = element.querySelector('[data-product-template-id]') !== null;
    
    // Vérifier qu'on a au moins 2 éléments de page produit
    const productElementsCount = [hasQuantityField, hasAddButton, hasProductPrice, hasJsProduct, hasProductTemplateId]
        .filter(Boolean).length;
    
    if (productElementsCount < 2) {
        return false;
    }
    
    const productId = getProductId(element);
    if (!productId) {
        return false;
    }
    
    if (window.priceBreakProcessed.has(productId)) {
        element.dataset.priceBreakProcessed = 'true';
        return false;
    }
    
    element.dataset.priceBreakProcessed = 'true';
    window.priceBreakProcessed.add(productId);
    
    addPriceBreakTable(element, productId);
    return true;
}

function getProductId(element) {
    const selectors = [
        'input[name="add_qty"]',
        'input[name="quantity"]',
        'input[id*="quantity"]',
        '.js_product input[name="add_qty"]',
        '.js_product input[name="quantity"]',
        'input[data-product-template-id]',
        'input[type="number"]',
        '.js_product input[type="number"]',
        '.product input[type="number"]'
    ];
    
    for (const selector of selectors) {
        const input = element.querySelector(selector);
        if (input) {
            return input.value;
        }
    }
    
    const productId = element.querySelector('[data-product-template-id]');
    if (productId) {
        return productId.dataset.productTemplateId;
    }
    
    const dataId = element.querySelector('[data-product-id]');
    if (dataId) {
        return dataId.dataset.productId;
    }
        
        return null;
    }

function addPriceBreakTable(container, productId) {
    const tableContainer = document.createElement('div');
    tableContainer.className = 'price-break-table-widget';
    tableContainer.dataset.productId = productId;
    
    const targetLocation = findTargetLocation(container);
    if (targetLocation) {
        targetLocation.appendChild(tableContainer);
        
        const widget = new SimplePriceBreakWidget(tableContainer);
        window.priceBreakWidget = widget;
    }
}

function findTargetLocation(container) {
    const selectors = [
        '.product_price',
        '.oe_product_price',
        '.price',
        '.product_details',
        '.product_info'
    ];
    
    for (const selector of selectors) {
        const element = container.querySelector(selector);
        if (element) {
            const wrapper = document.createElement('div');
            wrapper.className = 'price-break-wrapper';
            element.parentNode.insertBefore(wrapper, element.nextSibling);
            return wrapper;
        }
    }
    
    return container;
}

// Widget principal
class SimplePriceBreakWidget {
    constructor(element) {
        this.element = element;
        this.productId = element.dataset.productId;
        this.init();
    }
    
    async init() {
        this.showLoading();
        await this.loadData();
        this.setupQuantityChangeListener();
    }
    
    async loadData() {
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
                        args: [this.productId],
                        kwargs: {
                            pricelist_id: 1,
                            partner_id: null,
                            quantity: 1,
                        }
                    },
                    id: Math.floor(Math.random() * 1000000)
                })
            });
            
            const result = await response.json();
            
            if (result.result && result.result.rows && result.result.rows.length > 0) {
                this.renderTable(result.result);
            } else {
                this.renderEmpty();
            }
        } catch (error) {
            this.renderError();
        }
    }
    
    showLoading() {
        this.element.innerHTML = `
            <div class="price-break-table-loading">
                <small>Chargement des prix dégressifs...</small>
            </div>
        `;
    }

    renderTable(data) {
        const currentQuantity = this.getCurrentQuantity();
        const activeRow = this.findActiveRow(data.rows, currentQuantity);
        
        const rowsHtml = data.rows.map((row, index) => {
            const isActive = activeRow && activeRow.min_quantity === row.min_quantity;
            const activeClass = isActive ? ' price-break-active' : '';
            const boldQuantity = isActive ? `<strong>${row.quantity_display}</strong>` : row.quantity_display;
            const boldPrice = isActive ? `<strong>${row.price_formatted}</strong>` : row.price_formatted;
            
        return `
            <tr class="price-break-clickable${activeClass}" 
                data-quantity="${row.min_quantity}" 
                data-price="${row.price}"
                onclick="priceBreakWidget.setQuantity(${row.min_quantity})">
                <td>${boldQuantity}</td>
                <td class="text-right">${boldPrice}</td>
            </tr>
        `;
        }).join('');
        
        this.element.innerHTML = `
            <div class="price-break-table-container">
                <h6 class="price-break-table-title">
                    📊 Prix dégressifs par quantité
                </h6>
                <table class="price-break-table">
                    <thead>
                            <tr>
                                <th>Quantité</th>
                            <th class="text-right">Prix unitaire</th>
                            </tr>
                        </thead>
                        <tbody>
                        ${rowsHtml}
                        </tbody>
                    </table>
                <small class="price-break-help">
                    💡 Cliquez sur une ligne pour ajuster la quantité
                </small>
            </div>
        `;
        
        this.tableData = data;
    }
    
    renderEmpty() {
        this.element.innerHTML = `
            <div class="price-break-table-empty">
                <small>Aucun prix dégressif disponible pour ce produit.</small>
            </div>
        `;
    }
    
    renderError() {
        this.element.innerHTML = `
            <div class="price-break-table-error">
                <small>Erreur lors du chargement des prix dégressifs.</small>
            </div>
        `;
    }
    
    getCurrentQuantity() {
        const quantityInput = this.findQuantityInput();
        if (quantityInput && quantityInput.value) {
            return parseFloat(quantityInput.value);
        }
        return 1;
    }
    
    findActiveRow(rows, currentQuantity) {
        let activeRow = null;
        let maxMinQuantity = 0;
        
        for (const row of rows) {
            if (row.min_quantity <= currentQuantity && row.min_quantity > maxMinQuantity) {
                activeRow = row;
                maxMinQuantity = row.min_quantity;
            }
        }
        
        return activeRow;
    }
    
    setQuantity(quantity) {
        const quantityInput = this.findQuantityInput();
        if (quantityInput) {
            quantityInput.value = quantity;
            quantityInput.dispatchEvent(new Event('change', { bubbles: true }));
            quantityInput.dispatchEvent(new Event('input', { bubbles: true }));
            
            this.loadData();
            this.showQuantityUpdateMessage(quantity);
        }
    }
    
    findQuantityInput() {
        const selectors = [
            'input[name="add_qty"]',
            'input[name="quantity"]',
            'input[id*="quantity"]',
            '.js_product input[name="add_qty"]',
            '.js_product input[name="quantity"]',
            'input[data-product-template-id]',
            'input[type="number"]',
            '.js_product input[type="number"]',
            '.product input[type="number"]'
        ];
        
        for (const selector of selectors) {
            const input = document.querySelector(selector);
            if (input) {
                return input;
            }
        }
        
        const allInputs = document.querySelectorAll('input[type="number"]');
        for (let i = 0; i < allInputs.length; i++) {
            const input = allInputs[i];
            if (input.name && (input.name.includes('qty') || input.name.includes('quantity'))) {
                return input;
            }
        }
        
        return null;
    }
    
    setupQuantityChangeListener() {
        const quantityInput = this.findQuantityInput();
        if (quantityInput) {
            let updateTimeout;
            const updateTable = (event) => {
                clearTimeout(updateTimeout);
                updateTimeout = setTimeout(() => {
                    this.updateActiveRow();
                }, 300);
            };
            
            quantityInput.addEventListener('input', updateTable);
            quantityInput.addEventListener('change', updateTable);
            quantityInput.addEventListener('keyup', updateTable);
            
            const quantityContainer = quantityInput.closest('.input-group') || quantityInput.parentNode;
            if (quantityContainer) {
                quantityContainer.addEventListener('click', (event) => {
                    if (event.target.classList.contains('btn') || 
                        event.target.tagName === 'BUTTON' ||
                        event.target.classList.contains('fa-plus') ||
                        event.target.classList.contains('fa-minus')) {
                        setTimeout(updateTable, 100);
                    }
                });
                
                quantityContainer.addEventListener('change', updateTable);
            }
            
            this.quantityInput = quantityInput;
        } else {
            setTimeout(() => {
                this.setupQuantityChangeListener();
            }, 2000);
        }
    }
    
    updateActiveRow() {
        if (this.tableData && this.tableData.rows) {
            const currentQuantity = this.getCurrentQuantity();
            const activeRow = this.findActiveRow(this.tableData.rows, currentQuantity);
            
            const rows = this.element.querySelectorAll('tbody tr');
            
            rows.forEach((row, index) => {
                const rowData = this.tableData.rows[index];
                const isActive = activeRow && activeRow.min_quantity === rowData.min_quantity;
                
                if (isActive) {
                    row.classList.add('price-break-active');
                    row.classList.remove('price-break-clickable');
                    
                    const cells = row.querySelectorAll('td');
                    cells[0].innerHTML = `<strong>${rowData.quantity_display}</strong>`;
                    cells[1].innerHTML = `<strong>${rowData.price_formatted}</strong>`;
                } else {
                    row.classList.remove('price-break-active');
                    row.classList.add('price-break-clickable');
                    
                    const cells = row.querySelectorAll('td');
                    cells[0].innerHTML = rowData.quantity_display;
                    cells[1].innerHTML = rowData.price_formatted;
                }
            });
        }
    }
    
    showQuantityUpdateMessage(quantity) {
        const message = document.createElement('div');
        message.className = 'price-break-message';
        message.textContent = `Quantité mise à jour: ${quantity}`;
        
        document.body.appendChild(message);
        
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        }, 3000);
    }
}

// Initialisation
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPriceBreak);
} else {
    initPriceBreak();
}

// Export global pour debug
window.PriceBreak = {
    init: initPriceBreak,
    widget: SimplePriceBreakWidget
};