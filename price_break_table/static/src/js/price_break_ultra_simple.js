// Version ultra-simple du tableau de prix dégressifs
console.log('[PriceBreak] Script chargé');

// Fonction pour vérifier si on est sur une page produit
function isProductPage() {
    // Vérifier l'URL
    const url = window.location.href;
    console.log('[PriceBreak] URL actuelle:', url);
    
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
        '/shop/cart', // Panier
        '/shop/checkout', // Checkout
        '/cart', // Panier alternatif
        '/checkout' // Checkout alternatif
    ];
    
    const isNonProductPage = nonProductPages.some(path => url.includes(path));
    
    // Si on a des éléments de produit, on est probablement sur une page produit
    const result = hasProductElements || (isProductUrl && !isNonProductPage);
    
    console.log('[PriceBreak] Détection page produit:', {
        url,
        isProductUrl,
        hasProductElements,
        isNonProductPage,
        result,
        foundElements: productPageElements.filter(selector => 
            document.querySelector(selector) !== null
        )
    });
    
    return result;
}

// Fonction principale
function initPriceBreak() {
    console.log('[PriceBreak] Initialisation...');
    
    // Vérifier si on est sur une page produit
    if (!isProductPage()) {
        console.log('[PriceBreak] Pas sur une page produit, arrêt');
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

// Variable globale pour éviter les doublons
window.priceBreakProcessed = window.priceBreakProcessed || new Set();

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
    
    // Vérifier si ce produit a déjà été traité
    if (window.priceBreakProcessed.has(productId)) {
        console.log('[PriceBreak] Produit', productId, 'déjà traité, ignoré');
        element.dataset.priceBreakProcessed = 'true';
        return false;
    }
    
    // Marquer comme traité
    element.dataset.priceBreakProcessed = 'true';
    window.priceBreakProcessed.add(productId);
    
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
        
        // Initialiser le widget et le rendre accessible globalement
        const widget = new SimplePriceBreakWidget(tableContainer);
        window.priceBreakWidget = widget;
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
        this.setupQuantityChangeListener();
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
            
            if (result.result) {
                console.log('[PriceBreak] Données détaillées:', JSON.stringify(result.result, null, 2));
                
                if (result.result.rows && result.result.rows.length > 0) {
                    console.log('[PriceBreak] Tableau affiché avec', result.result.rows.length, 'lignes');
                    this.renderTable(result.result);
                } else {
                    console.log('[PriceBreak] Aucune ligne trouvée dans result.rows');
                    console.log('[PriceBreak] Structure complète:', result.result);
                    this.renderEmpty();
                }
            } else {
                console.log('[PriceBreak] Aucun résultat dans la réponse');
                this.renderError();
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
                <td><strong>${row.quantity_display}</strong></td>
                <td style="text-align: right;"><strong>${row.price_formatted}</strong></td>
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
        // Récupérer la quantité actuelle depuis le champ de saisie
        const quantityInput = this.findQuantityInput();
        if (quantityInput && quantityInput.value) {
            const quantity = parseFloat(quantityInput.value);
            console.log('[PriceBreak] Quantité actuelle détectée:', quantity);
            return quantity;
        }
        return 1; // Valeur par défaut
    }
    
    findActiveRow(rows, currentQuantity) {
        // Trouver la ligne active basée sur la quantité actuelle
        // La ligne active est celle dont la quantité minimale est la plus élevée
        // mais qui reste inférieure ou égale à la quantité actuelle
        let activeRow = null;
        let maxMinQuantity = 0;
        
        for (const row of rows) {
            if (row.min_quantity <= currentQuantity && row.min_quantity > maxMinQuantity) {
                activeRow = row;
                maxMinQuantity = row.min_quantity;
            }
        }
        
        console.log('[PriceBreak] Ligne active trouvée:', activeRow ? `Qty: ${activeRow.min_quantity}, Prix: ${activeRow.price_formatted}` : 'Aucune');
        return activeRow;
    }
    
    setQuantity(quantity) {
        console.log('[PriceBreak] Définition de la quantité:', quantity);
        
        // Trouver le champ de quantité sur la page
        const quantityInput = this.findQuantityInput();
        if (quantityInput) {
            quantityInput.value = quantity;
            quantityInput.dispatchEvent(new Event('change', { bubbles: true }));
            quantityInput.dispatchEvent(new Event('input', { bubbles: true }));
            
            console.log('[PriceBreak] Quantité mise à jour:', quantity);
            
            // Mettre à jour l'affichage du tableau
            this.loadData();
            
            // Optionnel: Afficher un message de confirmation
            this.showQuantityUpdateMessage(quantity);
        } else {
            console.log('[PriceBreak] Champ de quantité non trouvé');
        }
    }
    
    findQuantityInput() {
        // Sélecteurs pour trouver le champ de quantité
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
        
        console.log('[PriceBreak] Recherche du champ de quantité...');
        
        for (const selector of selectors) {
            const input = document.querySelector(selector);
            if (input) {
                console.log('[PriceBreak] Champ de quantité trouvé:', selector, input);
                console.log('[PriceBreak] Valeur actuelle:', input.value);
                return input;
            }
        }
        
        // Recherche plus large si aucun sélecteur spécifique ne fonctionne
        const allInputs = document.querySelectorAll('input[type="number"]');
        console.log('[PriceBreak] Tous les champs number trouvés:', allInputs.length);
        
        for (let i = 0; i < allInputs.length; i++) {
            const input = allInputs[i];
            console.log(`[PriceBreak] Input ${i}:`, input.name, input.id, input.value, input);
            
            // Vérifier si c'est probablement un champ de quantité
            if (input.name && (input.name.includes('qty') || input.name.includes('quantity'))) {
                console.log('[PriceBreak] Champ de quantité trouvé par nom:', input.name);
                return input;
            }
        }
        
        console.log('[PriceBreak] Aucun champ de quantité trouvé');
        return null;
    }
    
    setupQuantityChangeListener() {
        console.log('[PriceBreak] Configuration de l\'écouteur de changement de quantité...');
        
        // Écouter les changements de quantité manuels
        const quantityInput = this.findQuantityInput();
        if (quantityInput) {
            console.log('[PriceBreak] Écouteur de changement de quantité configuré sur:', quantityInput);
            
            // Fonction de mise à jour avec debounce pour éviter trop d'appels
            let updateTimeout;
            const updateTable = (event) => {
                if (event) {
                    console.log('[PriceBreak] Événement détecté:', event.type, 'Valeur:', event.target ? event.target.value : 'N/A');
                } else {
                    console.log('[PriceBreak] Mise à jour déclenchée (sans événement)');
                }
                clearTimeout(updateTimeout);
                updateTimeout = setTimeout(() => {
                    console.log('[PriceBreak] Changement de quantité détecté, mise à jour du tableau');
                    this.updateActiveRow();
                }, 300); // Attendre 300ms après le dernier changement
            };
            
            // Écouter différents types d'événements
            quantityInput.addEventListener('input', updateTable);
            quantityInput.addEventListener('change', updateTable);
            quantityInput.addEventListener('keyup', updateTable);
            
            // Écouter aussi les événements sur les boutons +/- (spinner)
            const quantityContainer = quantityInput.closest('.input-group') || quantityInput.parentNode;
            if (quantityContainer) {
                console.log('[PriceBreak] Ajout d\'écouteurs sur le conteneur de quantité');
                
                // Écouter les clics sur les boutons
                quantityContainer.addEventListener('click', (event) => {
                    if (event.target.classList.contains('btn') || 
                        event.target.tagName === 'BUTTON' ||
                        event.target.classList.contains('fa-plus') ||
                        event.target.classList.contains('fa-minus')) {
                        console.log('[PriceBreak] Clic sur bouton +/- détecté');
                        setTimeout(updateTable, 100); // Petit délai pour laisser la valeur se mettre à jour
                    }
                });
                
                // Écouter aussi les événements de changement sur le conteneur
                quantityContainer.addEventListener('change', updateTable);
            }
            
            // Test immédiat pour vérifier que l'écouteur fonctionne
            console.log('[PriceBreak] Test de l\'écouteur - valeur actuelle:', quantityInput.value);
            
            // Stocker la référence pour pouvoir la supprimer plus tard
            this.quantityInput = quantityInput;
        } else {
            console.log('[PriceBreak] Champ de quantité non trouvé pour l\'écouteur');
            
            // Essayer de reconfigurer après un délai au cas où le DOM n'est pas encore prêt
            setTimeout(() => {
                console.log('[PriceBreak] Tentative de reconfiguration de l\'écouteur...');
                this.setupQuantityChangeListener();
            }, 2000);
        }
    }
    
    updateActiveRow() {
        console.log('[PriceBreak] updateActiveRow appelée');
        
        // Mettre à jour uniquement l'affichage de la ligne active sans recharger toutes les données
        if (this.tableData && this.tableData.rows) {
            const currentQuantity = this.getCurrentQuantity();
            console.log('[PriceBreak] Quantité actuelle:', currentQuantity);
            
            const activeRow = this.findActiveRow(this.tableData.rows, currentQuantity);
            console.log('[PriceBreak] Ligne active trouvée:', activeRow);
            
            // Mettre à jour les styles des lignes
            const rows = this.element.querySelectorAll('tbody tr');
            console.log('[PriceBreak] Lignes trouvées:', rows.length);
            
            rows.forEach((row, index) => {
                const rowData = this.tableData.rows[index];
                const isActive = activeRow && activeRow.min_quantity === rowData.min_quantity;
                
                console.log(`[PriceBreak] Ligne ${index}: qty=${rowData.min_quantity}, active=${isActive}`);
                
                if (isActive) {
                    row.style.backgroundColor = '#e8f5e8';
                    row.style.border = '2px solid #28a745';
                    console.log(`[PriceBreak] Ligne ${index} mise en surbrillance`);
                } else {
                    row.style.backgroundColor = '';
                    row.style.border = '';
                }
            });
            
            console.log('[PriceBreak] Ligne active mise à jour pour quantité:', currentQuantity);
        } else {
            console.log('[PriceBreak] Pas de données de tableau disponibles pour la mise à jour');
        }
    }
    
    showQuantityUpdateMessage(quantity) {
        // Créer un message temporaire
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
        
        // Supprimer le message après 3 secondes
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

console.log('[PriceBreak] Script initialisé');
