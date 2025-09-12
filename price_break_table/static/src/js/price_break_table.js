/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useState, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PriceBreakTable extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            tableData: null,
            loading: false,
            currentQuantity: 1,
        });
        this.tableRef = useRef("table");
        
        onMounted(() => {
            this.loadTableData();
            this.setupQuantityListener();
        });
        
        onWillUnmount(() => {
            this.removeQuantityListener();
        });
    }

    get productId() {
        return this.props.productId || this.getProductIdFromPage();
    }

    get pricelistId() {
        return this.props.pricelistId || this.getPricelistIdFromPage();
    }

    get partnerId() {
        return this.props.partnerId || this.getPartnerIdFromPage();
    }

    async loadTableData(quantity = null) {
        if (!this.productId) return;
        
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "product.template",
                "get_price_break_table_js_data",
                [this.productId],
                {
                    pricelist_id: this.pricelistId,
                    partner_id: this.partnerId,
                    quantity: quantity || this.state.currentQuantity,
                }
            );
            
            this.state.tableData = data;
            if (quantity !== null) {
                this.state.currentQuantity = quantity;
            }
            
            // Mise à jour de la surbrillance après un court délai
            setTimeout(() => {
                this.highlightActiveRow();
            }, 100);
            
        } catch (error) {
            console.error("Erreur lors du chargement du tableau de prix:", error);
        } finally {
            this.state.loading = false;
        }
    }

    setupQuantityListener() {
        // Écoute des changements de quantité dans les inputs du panier
        const quantityInputs = document.querySelectorAll('input[name="add_qty"], input[name="quantity"]');
        quantityInputs.forEach(input => {
            input.addEventListener('input', this.onQuantityChange.bind(this));
            input.addEventListener('change', this.onQuantityChange.bind(this));
        });
    }

    removeQuantityListener() {
        const quantityInputs = document.querySelectorAll('input[name="add_qty"], input[name="quantity"]');
        quantityInputs.forEach(input => {
            input.removeEventListener('input', this.onQuantityChange.bind(this));
            input.removeEventListener('change', this.onQuantityChange.bind(this));
        });
    }

    onQuantityChange(event) {
        const newQuantity = parseFloat(event.target.value) || 1;
        if (newQuantity !== this.state.currentQuantity) {
            this.state.currentQuantity = newQuantity;
            this.loadTableData(newQuantity);
        }
    }

    async onRowClick(row) {
        if (!row.min_quantity) return;
        
        // Mise à jour de la quantité dans l'input
        const quantityInput = document.querySelector('input[name="add_qty"], input[name="quantity"]');
        if (quantityInput) {
            quantityInput.value = row.min_quantity;
            quantityInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        // Mise à jour de l'état local
        this.state.currentQuantity = row.min_quantity;
        await this.loadTableData(row.min_quantity);
    }

    highlightActiveRow() {
        if (!this.tableRef.el || !this.state.tableData) return;
        
        const rows = this.tableRef.el.querySelectorAll('tbody tr');
        rows.forEach((row, index) => {
            const rowData = this.state.tableData.rows[index];
            if (rowData && rowData.is_active) {
                row.classList.add('price-break-active');
            } else {
                row.classList.remove('price-break-active');
            }
        });
    }

    getProductIdFromPage() {
        // Tentative de récupération de l'ID produit depuis la page
        const productIdInput = document.querySelector('input[name="product_template_id"]');
        if (productIdInput) return parseInt(productIdInput.value);
        
        const productIdMeta = document.querySelector('meta[name="product-id"]');
        if (productIdMeta) return parseInt(productIdMeta.content);
        
        // Extraction depuis l'URL ou d'autres éléments
        const urlMatch = window.location.pathname.match(/\/product\/(\d+)/);
        if (urlMatch) return parseInt(urlMatch[1]);
        
        return null;
    }

    getPricelistIdFromPage() {
        const pricelistInput = document.querySelector('input[name="pricelist_id"]');
        if (pricelistInput) return parseInt(pricelistInput.value);
        
        const pricelistMeta = document.querySelector('meta[name="pricelist-id"]');
        if (pricelistMeta) return parseInt(pricelistMeta.content);
        
        return null;
    }

    getPartnerIdFromPage() {
        const partnerInput = document.querySelector('input[name="partner_id"]');
        if (partnerInput) return parseInt(partnerInput.value);
        
        return null;
    }

    render() {
        if (this.state.loading) {
            return this.renderLoading();
        }
        
        if (!this.state.tableData || !this.state.tableData.rows.length) {
            return this.renderEmpty();
        }
        
        return this.renderTable();
    }

    renderLoading() {
        return `
            <div class="price-break-table-loading">
                <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <span class="ms-2">Chargement des prix...</span>
            </div>
        `;
    }

    renderEmpty() {
        return `
            <div class="price-break-table-empty">
                <p class="text-muted mb-0">Aucun prix dégressif disponible pour ce produit.</p>
            </div>
        `;
    }

    renderTable() {
        const { rows, currency } = this.state.tableData;
        
        return `
            <div class="price-break-table-container">
                <h6 class="price-break-table-title">
                    <i class="fa fa-table me-2"></i>
                    Prix dégressifs par quantité
                </h6>
                <div class="table-responsive">
                    <table class="table table-sm table-hover price-break-table" ref="table">
                        <thead class="table-light">
                            <tr>
                                <th>Quantité</th>
                                <th class="text-end">Prix unitaire</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows.map(row => this.renderTableRow(row)).join('')}
                        </tbody>
                    </table>
                </div>
                <small class="text-muted">
                    <i class="fa fa-info-circle me-1"></i>
                    Cliquez sur une ligne pour ajuster la quantité
                </small>
            </div>
        `;
    }

    renderTableRow(row) {
        const activeClass = row.is_active ? 'price-break-active' : '';
        const clickableClass = 'price-break-clickable';
        
        return `
            <tr class="${activeClass} ${clickableClass}" 
                data-min-qty="${row.min_quantity}" 
                data-max-qty="${row.max_quantity || ''}"
                onclick="this.onRowClick(${JSON.stringify(row).replace(/"/g, '&quot;')})">
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
}

// Enregistrement du composant
registry.category("public_components").add("price_break_table", PriceBreakTable);

// Fonction globale pour l'interaction avec les lignes
window.onRowClick = function(row) {
    const event = new CustomEvent('price-break-row-click', {
        detail: { row: row }
    });
    document.dispatchEvent(event);
};
