/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { Component } from "@odoo/owl";

// Patch pour ajouter des fonctionnalités spécifiques aux fiches commerciales
patch(FormController.prototype, {
    
    /**
     * Surcharge pour ajouter des actions spécifiques aux fiches commerciales
     */
    async setup() {
        super.setup();
        this.setupCommercialSheetActions();
    },
    
    setupCommercialSheetActions() {
        // Ajouter des actions spécifiques si on est sur une fiche commerciale
        if (this.model.root.resModel === 'product.commercial.sheet') {
            this.addCommercialSheetShortcuts();
        }
    },
    
    addCommercialSheetShortcuts() {
        // Raccourcis clavier pour les fiches commerciales
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey && event.key === 's') {
                event.preventDefault();
                this.saveRecord();
            }
        });
    },
    
    /**
     * Action personnalisée pour générer le PDF
     */
    async actionGeneratePDF() {
        const record = this.model.root;
        if (record.resId) {
            // Appeler l'action de génération PDF
            await this.env.services.action.doAction({
                type: 'ir.actions.report',
                report_name: 'product_commercial_sheet.report_commercial_sheet',
                report_type: 'qweb-pdf',
                data: { ids: [record.resId] },
                context: this.env.context,
            });
        }
    }
});

// Widget personnalisé pour les champs de fiche commerciale
export class CommercialSheetField extends Component {
    static template = "product_commercial_sheet.CommercialSheetField";
    
    setup() {
        super.setup();
        this.setupFieldValidation();
    }
    
    setupFieldValidation() {
        // Validation personnalisée pour les champs
        this.props.record.on('update', this.validateField.bind(this));
    }
    
    validateField() {
        const fieldName = this.props.name;
        const value = this.props.record.data[fieldName];
        
        // Validation spécifique selon le type de champ
        if (fieldName.startsWith('custom_field_')) {
            this.validateCustomField(fieldName, value);
        }
    }
    
    validateCustomField(fieldName, value) {
        // Validation des champs personnalisés
        if (fieldName === 'custom_field_5' && value && value < 0) {
            this.env.services.notification.add('La valeur ne peut pas être négative', {
                type: 'warning'
            });
        }
    }
}

// Enregistrement du widget
registry.category("view_widgets").add("commercial_sheet_field", CommercialSheetField);
