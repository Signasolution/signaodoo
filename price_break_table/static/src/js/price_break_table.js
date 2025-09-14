// Tableau de prix dégressifs pour Odoo - Version unifiée
// Toutes les fonctionnalités dans un seul fichier

// Fonction pour vérifier si on est sur une page produit du site web
function isProductPage() {
    // 1. Vérifier qu'on est sur le site web (pas le backend)
    if (document.querySelector('.o_web_client')) {
        return false; // Backend Odoo
    }
    
    // 2. Utiliser les données de session Odoo pour détecter une page produit
    try {
        // Vérifier si on a accès à l'objet session d'Odoo
        if (typeof odoo !== 'undefined' && odoo.session) {
            const session = odoo.session;
            
            // Vérifier si on est sur une page produit via les données de session
            if (session.website && session.website.current_website) {
                // Vérifier les paramètres de la page actuelle
                const currentPage = session.website.current_website;
                if (currentPage && currentPage.product_tmpl_id) {
                    return true;
                }
            }
        }
        
        // 3. Vérifier via les données globales d'Odoo
        if (typeof odoo !== 'undefined' && odoo.website) {
            const website = odoo.website;
            if (website.product && website.product.product_tmpl_id) {
                return true;
            }
        }
        
        // 4. Vérifier via les données de la page dans le DOM (méta tags)
        const productMeta = document.querySelector('meta[name="product-template-id"]');
        if (productMeta && productMeta.content) {
            return true;
        }
        
        // 5. Vérifier via les données JSON dans le DOM
        const productData = document.querySelector('script[type="application/json"][data-product]');
        if (productData) {
            try {
                const data = JSON.parse(productData.textContent);
                if (data.product_tmpl_id || data.product_id) {
                    return true;
                }
            } catch (e) {
                // Ignorer les erreurs de parsing
            }
        }
        
        // 6. Vérifier via les attributs data spécifiques aux pages produit
        const productTemplateData = document.querySelector('[data-product-template-id]');
        if (productTemplateData && productTemplateData.dataset.productTemplateId) {
            return true;
        }
        
        // 7. Vérifier via les variables globales JavaScript d'Odoo
        if (typeof window.product_tmpl_id !== 'undefined' && window.product_tmpl_id) {
            return true;
        }
        
        if (typeof window.product_id !== 'undefined' && window.product_id) {
            return true;
        }
        
    } catch (error) {
        // En cas d'erreur, ne pas afficher le tableau
        return false;
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
    
    // Si on arrive ici, c'est que isProductPage() a déjà validé qu'on est sur une page produit
    // On peut donc traiter l'élément directement
    
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