// Version ultra-simple du tableau de prix dégressifs
console.log('[PriceBreak] Script chargé');

// Fonction principale
function initPriceBreak() {
    console.log('[PriceBreak] Initialisation...');
    
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
        console.log(`[PriceBreak] Sélecteur ${selector}: ${elements.length} élément(s) trouvé(s)`);
        
        elements.forEach(element => {
            if (processProductElement(element)) {
                foundProducts = true;
            }
        });
    }
    
    if (!foundProducts) {
        console.log('[PriceBreak] Aucun produit trouvé, nouvelle tentative dans 2s...');
        setTimeout(initPriceBreak, 2000);
    }
}

function processProductElement(element) {
    // Vérifier si déjà traité
    if (element.dataset.priceBreakProcessed) {
        return false;
    }
    
    console.log('[PriceBreak] Traitement de l\'élément:', element);
    
    const productId = getProductId(element);
    if (!productId) {
        console.log('[PriceBreak] ID produit non trouvé pour l\'élément');
        return false;
    }
    
    console.log('[PriceBreak] ID produit trouvé:', productId);
    
    // Marquer comme traité
    element.dataset.priceBreakProcessed = 'true';
    
    // Ajouter le tableau
    addPriceBreakTable(element, productId);
    
    return true;
}

function getProductId(element) {
    console.log('[PriceBreak] Recherche de l\'ID produit...');
    
    // Méthode 1: Input hidden
    const productInput = document.querySelector('input[name="product_template_id"]');
    if (productInput && productInput.value) {
        console.log('[PriceBreak] ID trouvé via input:', productInput.value);
        return productInput.value;
    }
    
    // Méthode 2: Data attribute
    const dataElement = document.querySelector('[data-product-template-id]');
    if (dataElement && dataElement.dataset.productTemplateId) {
        console.log('[PriceBreak] ID trouvé via data:', dataElement.dataset.productTemplateId);
        return dataElement.dataset.productTemplateId;
    }
    
    // Méthode 3: URL
    const urlMatch = window.location.pathname.match(/\/product\/(\d+)/);
    if (urlMatch) {
        console.log('[PriceBreak] ID trouvé via URL:', urlMatch[1]);
        return urlMatch[1];
    }
    
    console.log('[PriceBreak] Aucun ID produit trouvé');
    return null;
}

function addPriceBreakTable(container, productId) {
    console.log('[PriceBreak] Ajout du tableau pour le produit:', productId);
    
    // Créer le conteneur
    const tableContainer = document.createElement('div');
    tableContainer.className = 'price-break-table-widget';
    tableContainer.dataset.productId = productId;
    tableContainer.style.marginTop = '20px';
    
    // Trouver l'emplacement
    const targetLocation = findTargetLocation(container);
    if (targetLocation) {
        targetLocation.appendChild(tableContainer);
        
        // Initialiser le widget
        new SimplePriceBreakWidget(tableContainer);
        console.log('[PriceBreak] Tableau ajouté avec succès');
    } else {
        console.log('[PriceBreak] Emplacement non trouvé');
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

// Widget simple
class SimplePriceBreakWidget {
    constructor(element) {
        this.element = element;
        this.productId = element.dataset.productId;
        console.log('[PriceBreak] Widget créé pour le produit:', this.productId);
        
        this.init();
    }
    
    async init() {
        this.showLoading();
        await this.loadData();
    }
    
    async loadData() {
        console.log('[PriceBreak] Chargement des données pour:', this.productId);
        
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
                            pricelist_id: 1,
                            partner_id: null,
                            quantity: 1,
                        }
                    },
                    id: Math.floor(Math.random() * 1000000)
                })
            });
            
            const result = await response.json();
            console.log('[PriceBreak] Réponse reçue:', result);
            
            if (result.result && result.result.rows && result.result.rows.length > 0) {
                console.log('[PriceBreak] Tableau affiché avec', result.result.rows.length, 'lignes');
                this.renderTable(result.result);
            } else {
                console.log('[PriceBreak] Aucune donnée trouvée');
                this.renderEmpty();
            }
            
        } catch (error) {
            console.error('[PriceBreak] Erreur:', error);
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
        const rowsHtml = data.rows.map(row => `
            <tr style="cursor: pointer; ${row.is_active ? 'background-color: #e8f5e8;' : ''}">
                <td><strong>${row.quantity_display}</strong></td>
                <td style="text-align: right;"><strong>${row.price_formatted}</strong></td>
            </tr>
        `).join('');
        
        this.element.innerHTML = `
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; background: #f9f9f9; margin: 10px 0;">
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

console.log('[PriceBreak] Script initialisé');
