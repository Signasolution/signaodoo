// Tableau de prix dégressifs pour Odoo
// Version de production - Code nettoyé

// Fonction pour vérifier si on est sur une page produit
function isProductPage() {
    const url = window.location.href;
    
    // Patterns d'URL qui indiquent qu'on est sur une page produit
    const productUrlPatterns = [
        /\/shop\/product\//,
        /\/product\//,
        /\/product\/\d+/,
        /\/shop\/product\/\d+/,
        /\?product=/,
        /#product/,
        /\/product-\d+/,
        /\/shop\/product-\d+/,
        /\/product\/\w+/,
        /\/shop\/product\/\w+/
    ];
    
    // Vérifier si l'URL correspond à un pattern de page produit
    const isProductUrl = productUrlPatterns.some(pattern => pattern.test(url));
    
    // Vérifier aussi les éléments DOM spécifiques à une page produit
    const productPageElements = [
        'input[name="add_qty"]',
        '.js_product',
        '.product_detail',
        '#product_detail',
        '.oe_website_sale',
        '[data-product-template-id]',
        '.js_main_product'
    ];
    
    const hasProductElements = productPageElements.some(selector => 
        document.querySelector(selector) !== null
    );
    
    // Vérifier qu'on n'est PAS sur une page de liste ou panier
    const nonProductPages = [
        '/shop/cart',
        '/shop/checkout',
        '/cart',
        '/checkout'
    ];
    
    const isNonProductPage = nonProductPages.some(path => url.includes(path));
    
    return hasProductElements || (isProductUrl && !isNonProductPage);
}

// Fonction principale
function initPriceBreak() {
    if (!isProductPage()) {
        return;
    }
    
    // Chercher tous les éléments de page produit
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
    // Essayer de trouver l'ID du produit de différentes façons
    const input = element.querySelector('input[name="add_qty"]');
    if (input) {
        return input.value;
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
    // Créer le conteneur
    const tableContainer = document.createElement('div');
    tableContainer.className = 'price-break-table-widget';
    tableContainer.dataset.productId = productId;
    tableContainer.style.marginTop = '20px';
    
    // Trouver l'emplacement
    const targetLocation = findTargetLocation(container);
    if (targetLocation) {
        targetLocation.appendChild(tableContainer);
        
        // Initialiser le widget et le rendre accessible globalement
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
            wrapper.style.marginTop = '15px';
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
            <div style="text-align: center; padding: 10px; border: 1px solid #ddd; background: #f9f9f9;">
                <small>Chargement des prix dégressifs...</small>
            </div>
        `;
    }
    
    renderTable(data) {
        // Trouver la ligne active basée sur la quantité actuelle
        const currentQuantity = this.getCurrentQuantity();
        const activeRow = this.findActiveRow(data.rows, currentQuantity);
        
        const rowsHtml = data.rows.map((row, index) => {
            const isActive = activeRow && activeRow.min_quantity === row.min_quantity;
            return `
            <tr style="cursor: pointer; ${isActive ? 'background-color: #e8f5e8; border: 2px solid #28a745;' : ''}" 
                data-quantity="${row.min_quantity}" 
                data-price="${row.price}"
                onclick="priceBreakWidget.setQuantity(${row.min_quantity})">
                <td>${isActive ? `<strong>${row.quantity_display}</strong>` : row.quantity_display}</td>
                <td style="text-align: right;">${isActive ? `<strong>${row.price_formatted}</strong>` : row.price_formatted}</td>
            </tr>
        `;
        }).join('');
        
        this.element.innerHTML = `
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; background: #f9f9f9; margin: 10px 0; width: 60%;">
                <h6 style="margin-bottom: 10px; color: #333;">
                    📊 Prix dégressifs par quantité
                </h6>
                <table class="table table-sm" style="margin-bottom: 10px; font-size: 0.9em; width: 100%;">
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
        
        // Stocker les données pour les utiliser dans setQuantity
        this.tableData = data;
    }
    
    renderEmpty() {
        this.element.innerHTML = `
            <div style="text-align: center; padding: 10px; color: #666; border: 1px solid #ddd; background: #f9f9f9;">
                <small>Aucun prix dégressif disponible pour ce produit.</small>
            </div>
        `;
    }
    
    renderError() {
        this.element.innerHTML = `
            <div style="text-align: center; padding: 10px; color: #d32f2f; border: 1px solid #ddd; background: #f9f9f9;">
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
        
        // Recherche plus large
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
            
            // Écouter différents types d'événements
            quantityInput.addEventListener('input', updateTable);
            quantityInput.addEventListener('change', updateTable);
            quantityInput.addEventListener('keyup', updateTable);
            
            // Écouter aussi les événements sur les boutons +/- (spinner)
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
            // Essayer de reconfigurer après un délai
            setTimeout(() => {
                this.setupQuantityChangeListener();
            }, 2000);
        }
    }
    
    updateActiveRow() {
        if (this.tableData && this.tableData.rows) {
            const currentQuantity = this.getCurrentQuantity();
            const activeRow = this.findActiveRow(this.tableData.rows, currentQuantity);
            
            // Mettre à jour les styles des lignes
            const rows = this.element.querySelectorAll('tbody tr');
            
            rows.forEach((row, index) => {
                const rowData = this.tableData.rows[index];
                const isActive = activeRow && activeRow.min_quantity === rowData.min_quantity;
                
                if (isActive) {
                    row.style.backgroundColor = '#e8f5e8';
                    row.style.border = '2px solid #28a745';
                    
                    // Mettre en gras le texte de la ligne active
                    const cells = row.querySelectorAll('td');
                    cells[0].innerHTML = `<strong>${rowData.quantity_display}</strong>`;
                    cells[1].innerHTML = `<strong>${rowData.price_formatted}</strong>`;
                } else {
                    row.style.backgroundColor = '';
                    row.style.border = '';
                    
                    // Retirer le gras du texte des lignes inactives
                    const cells = row.querySelectorAll('td');
                    cells[0].innerHTML = rowData.quantity_display;
                    cells[1].innerHTML = rowData.price_formatted;
                }
            });
        }
    }
    
    showQuantityUpdateMessage(quantity) {
        const message = document.createElement('div');
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            z-index: 9999;
            font-size: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        `;
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