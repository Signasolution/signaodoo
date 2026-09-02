/*
 * Page produit : minimum de commande et tableau de prix dégressifs.
 *
 * Chargé sur toutes les pages du site, mais ne fait rien tant que le markup
 * injecté par views/website_sale_templates.xml n'est pas présent.
 *
 * Le sélecteur de quantité est un composant Owl (sale.QuantityButtons) : il
 * réécrit la valeur de l'input en patchant le DOM, sans émettre d'évènement.
 * On intercepte donc la propriété « value » de l'input pour être notifié de ces
 * écritures programmatiques, plutôt que de scruter la valeur en boucle.
 */
(function () {
    "use strict";

    var nativeValue = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value");

    function onReady(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }

    /* Écrit une valeur en contournant le cache d'Owl, et prévient la page. */
    function setNative(input, val) {
        try {
            nativeValue.set.call(input, val);
        } catch (e) {
            input.value = val;
        }
        ["input", "change"].forEach(function (ev) {
            input.dispatchEvent(new Event(ev, { bubbles: true }));
        });
    }

    /*
     * Appelle `callback` à chaque changement de valeur de l'input, qu'il vienne
     * de l'utilisateur ou d'une écriture programmatique. Renvoie false si
     * l'interception n'a pas pu être posée, pour que l'appelant prévoie un
     * filet de sécurité.
     */
    function watchValue(input, callback) {
        ["input", "change", "blur"].forEach(function (ev) {
            input.addEventListener(ev, callback);
        });
        /* Couvre le cas où la valeur est posée via setAttribute plutôt que
           par la propriété interceptée ci-dessous. */
        try {
            new MutationObserver(callback).observe(input, {
                attributes: true,
                attributeFilter: ["value"]
            });
        } catch (e) {}
        try {
            Object.defineProperty(input, "value", {
                configurable: true,
                get: function () {
                    return nativeValue.get.call(this);
                },
                set: function (v) {
                    nativeValue.set.call(this, v);
                    callback();
                }
            });
            return true;
        } catch (e) {
            return false;
        }
    }

    /* Regroupe les appels rapprochés et laisse Owl finir son rendu avant d'agir. */
    function debounced(fn) {
        var pending = false;
        return function () {
            if (pending) {
                return;
            }
            pending = true;
            setTimeout(function () {
                pending = false;
                fn();
            }, 0);
        };
    }

    function init() {
        var minQtyEl = document.getElementById("price_break_min_qty_value");
        var rows = document.querySelectorAll(".price-break-row");
        if (!minQtyEl && !rows.length) {
            return;
        }

        var minQty = minQtyEl ? (parseFloat(minQtyEl.dataset.minQty) || 0) : 0;
        var minLabel = (minQty % 1 === 0 ? parseInt(minQty, 10) : minQty) + " unité(s)";
        var input = document.querySelector('input[name="add_qty"]');

        /* ---- Minimum de commande : page produit ---- */
        var errorBox = document.getElementById("price_break_min_qty_error");
        var errorTm = null;

        function showPageError() {
            if (!errorBox) {
                return;
            }
            errorBox.style.display = "block";
            clearTimeout(errorTm);
            errorTm = setTimeout(function () { errorBox.style.display = "none"; }, 5000);
        }

        /* ---- Tableau de prix dégressifs ---- */
        function highlight(qty) {
            var best = null;
            rows.forEach(function (r) {
                if (qty >= parseFloat(r.dataset.qty)) {
                    best = r;
                }
            });
            rows.forEach(function (r) { r.classList.remove("price-break-active"); });
            if (best) {
                best.classList.add("price-break-active");
            }
        }

        /* Seul point d'entrée réagissant à un changement de quantité. */
        var syncing = false;
        function sync() {
            if (syncing || !input) {
                return;
            }
            syncing = true;
            try {
                var qty = parseFloat(input.value);
                if (minQty > 0 && qty < minQty) {
                    showPageError();
                    setNative(input, minQty);
                    qty = minQty;
                }
                if (!isNaN(qty)) {
                    highlight(qty);
                }
            } finally {
                syncing = false;
            }
        }
        var scheduleSync = debounced(sync);

        if (input) {
            if (minQty > 0) {
                input.setAttribute("min", minQty);
                if (!input.value || parseFloat(input.value) < minQty) {
                    setNative(input, minQty);
                }
            }
            if (!watchValue(input, scheduleSync)) {
                // L'interception a échoué : on retombe sur une surveillance lente.
                setInterval(sync, 500);
            }
            sync();
        }

        rows.forEach(function (row) {
            row.addEventListener("click", function () {
                var qty = Math.max(parseFloat(row.dataset.qty), minQty || 0);
                if (input) {
                    setNative(input, qty);
                }
                highlight(qty);
            });
        });

        /* ---- Minimum de commande : modales de variantes ---- */
        /* Les modales sont montées à la volée : on les découvre via un observer
           plutôt qu'en scrutant le DOM en boucle. */
        if (minQty <= 0) {
            return;
        }

        var MODAL_SEL = [
            '.modal.show input[type="number"]',
            '.modal-dialog input[type="number"]',
            '.o_dialog input[type="number"]',
            '[role="dialog"] input[type="number"]',
            'dialog input[type="number"]'
        ].join(",");

        function modalCell(inp) {
            return inp.closest("td") || inp.closest(".input-group") || inp.parentNode;
        }

        function addModalLabel(inp) {
            var cell = modalCell(inp);
            if (!cell || cell.querySelector(".pb-modal-lbl")) {
                return;
            }
            var d = document.createElement("div");
            d.className = "pb-modal-lbl text-center text-muted mt-1";
            d.innerHTML = "Qté mini : <strong>" + minLabel + "</strong>";
            cell.appendChild(d);
        }

        function showModalErr(inp) {
            var cell = modalCell(inp);
            if (!cell || cell.querySelector(".pb-modal-err")) {
                return;
            }
            var d = document.createElement("div");
            d.className = "pb-modal-err text-center text-danger mt-1";
            d.innerHTML = "Qté minimale : <strong>" + minLabel + "</strong>";
            cell.appendChild(d);
            setTimeout(function () {
                if (d.parentNode) {
                    d.parentNode.removeChild(d);
                }
            }, 4000);
        }

        function scanModals() {
            var inputs;
            try {
                inputs = document.querySelectorAll(MODAL_SEL);
            } catch (e) {
                return;
            }
            inputs.forEach(function (inp) {
                addModalLabel(inp);
                if (!inp.dataset.pbInit) {
                    inp.dataset.pbInit = "1";
                    inp.setAttribute("min", minQty);
                    var enforce = debounced(function () {
                        if (parseFloat(inp.value) < minQty) {
                            showModalErr(inp);
                            setNative(inp, minQty);
                        }
                    });
                    watchValue(inp, enforce);
                }
                if (parseFloat(inp.value) < minQty) {
                    setNative(inp, minQty);
                }
            });
        }

        new MutationObserver(debounced(scanModals)).observe(document.body, {
            childList: true,
            subtree: true
        });
        scanModals();
    }

    onReady(init);
})();
