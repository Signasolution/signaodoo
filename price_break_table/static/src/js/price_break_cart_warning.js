/*
 * Affiche sans rechargement l'avertissement de quantité minimale renvoyé par
 * la surcharge de cart_update_json (controllers/main.py), en interceptant les
 * appels JSON-RPC vers le panier.
 */
(function () {
    "use strict";

    function showCartWarning(msg) {
        var id = "pb_cart_warning_toast";
        var box = document.getElementById(id);
        if (!box) {
            box = document.createElement("div");
            box.id = id;
            box.className = "pb-cart-warning-toast";
            document.body.appendChild(box);
        }
        box.innerHTML = '<span class="pb-cart-warning-icon">&#9888;</span>';
        box.appendChild(document.createTextNode(msg));
        box.style.display = "block";
        clearTimeout(box._t);
        box._t = setTimeout(function () { box.style.display = "none"; }, 6000);
    }

    function isCartUpdate(url) {
        var u = (url && url.toString) ? url.toString() : "";
        return u.indexOf("cart/update_json") !== -1 || u.indexOf("cart_update_json") !== -1;
    }

    function warningOf(data) {
        return (data && data.result && data.result.warning) || (data && data.warning);
    }

    /* Interception fetch (Odoo 18 utilise fetch pour les appels JSON-RPC) */
    var _fetch = window.fetch;
    window.fetch = function (url) {
        var p = _fetch.apply(this, arguments);
        try {
            if (isCartUpdate(url)) {
                p.then(function (resp) {
                    resp.clone().json().then(function (data) {
                        var w = warningOf(data);
                        if (w) {
                            showCartWarning(w);
                        }
                    }).catch(function () {});
                }).catch(function () {});
            }
        } catch (e) {}
        return p;
    };

    /* Interception XMLHttpRequest (fallback) */
    var _open = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function (method, url) {
        this._pbUrl = url || "";
        return _open.apply(this, arguments);
    };
    var _send = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function () {
        if (isCartUpdate(this._pbUrl)) {
            var self = this;
            this.addEventListener("load", function () {
                try {
                    var w = warningOf(JSON.parse(self.responseText));
                    if (w) {
                        showCartWarning(w);
                    }
                } catch (e) {}
            });
        }
        return _send.apply(this, arguments);
    };
})();
