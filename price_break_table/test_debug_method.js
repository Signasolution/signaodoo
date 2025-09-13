// Script de test pour la méthode debug
console.log('[DEBUG] Test de la méthode debug');

async function testDebugMethod() {
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
                    method: 'get_price_break_table_js_data_debug',
                    args: [2], // Produit ID 2
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
        console.log('[DEBUG] Résultat méthode debug:', result);
        
    } catch (error) {
        console.error('[DEBUG] Erreur:', error);
    }
}

// Exécuter le test
testDebugMethod();
