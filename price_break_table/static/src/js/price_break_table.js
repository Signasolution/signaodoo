/*
 * Page produit : minimum de commande et tableau de prix dégressifs.
 *
 * Chargé sur toutes les pages du site, mais ne fait rien tant que le markup
 * injecté par views/website_sale_templates.xml n'est pas présent.
 */
(function () {
    "use strict";

    function onReady(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }

    /* Setter natif : contourne le cache de valeur d'Owl. */
    function setNative(input, val) {
        try {
            var setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, "value").set;
            setter.call(input, val);
        } catch (e) {
            input.value = val;
        }
        ["input", "change"].forEach(function (ev) {
            input.dispatchEvent(new Event(ev, { bubbles: true }));
        });
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

        function enforcePageMin() {
            if (parseFloat(input.value) < minQty) {
                showPageError();
                setNative(input, minQty);
            }
        }

        if (input && minQty > 0) {
            input.setAttribute("min", minQty);
            if (!input.value || parseFloat(input.value) < minQty) {
                setNative(input, minQty);
            }
            input.addEventListener("change", enforcePageMin);
            input.addEventListener("blur", enforcePageMin);
            setInterval(enforcePageMin, 300);
        }

        /* ---- Minimum de commande : modales de variantes ---- */
        /* On cible tout input[type=number] dans un conteneur dialog ; l'input de
           la page produit elle-même n'est jamais dans un dialog. */
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

        function enforceModalMin(inp) {
            if (parseFloat(inp.value) < minQty) {
                showModalErr(inp);
                setNative(inp, minQty);
            }
        }

        if (minQty > 0) {
            setInterval(function () {
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
                        inp.addEventListener("change", function () { enforceModalMin(inp); });
                        inp.addEventListener("blur", function () { enforceModalMin(inp); });
                    }
                    var v = parseFloat(inp.value);
                    if (!isNaN(v) && v < minQty) {
                        setNative(inp, minQty);
                    }
                });
            }, 150);
        }

        /* ---- Tableau de prix dégressifs ---- */
        if (!rows.length) {
            return;
        }
        var last = input ? input.value : "";

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

        function onQtyChange() {
            if (input.value !== last) {
                last = input.value;
                var q = parseFloat(input.value);
                if (!isNaN(q)) {
                    highlight(q);
                }
            }
        }

        if (input) {
            input.addEventListener("input", onQtyChange);
            input.addEventListener("change", onQtyChange);
            setInterval(onQtyChange, 200);
            document.querySelectorAll("button,.btn,.fa-plus,.fa-minus,.btn-plus,.btn-minus").forEach(function (b) {
                b.addEventListener("click", function () { setTimeout(onQtyChange, 350); });
            });
        }

        rows.forEach(function (row) {
            row.addEventListener("click", function () {
                var qty = Math.max(parseFloat(row.dataset.qty), minQty || 0);
                if (input) {
                    setNative(input, qty);
                    last = qty.toString();
                }
                highlight(qty);
            });
        });
    }

    onReady(init);
})();
