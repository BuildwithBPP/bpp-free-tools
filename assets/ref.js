// Partner ref links. Reads ?ref=<code> (lowercase letters, digits, hyphens, max 40;
// anything else is ignored), keeps it for the browser session, and exposes
// window.bppRefFields() so each tool adds { name: "lm_ref", value: code } to its
// HubSpot submission. Shows "Shared by <name>" only for codes in assets/partners.js.
// Load partners.js first. Storage can be blocked (private mode), so every access is guarded.
(function () {
  var KEY = "bpp_ref";
  var VALID = /^[a-z0-9-]{1,40}$/;
  var code = null;

  var fromUrl = null;
  try { fromUrl = new URLSearchParams(window.location.search).get("ref"); } catch (e) {}
  if (fromUrl !== null && VALID.test(fromUrl)) {
    code = fromUrl;
    try { window.sessionStorage.setItem(KEY, code); } catch (e) {}
  } else {
    try {
      var saved = window.sessionStorage.getItem(KEY);
      if (saved && VALID.test(saved)) code = saved;
    } catch (e) {}
  }

  window.bppRefFields = function () {
    return code ? [{ name: "lm_ref", value: code }] : [];
  };

  var partners = window.BPP_PARTNERS || {};
  var name = code && Object.prototype.hasOwnProperty.call(partners, code) ? partners[code] : "";
  if (!name || typeof name !== "string") return;
  var wrap = document.querySelector(".wrap");
  if (!wrap) return;
  var line = document.createElement("p");
  line.className = "bpp-ref";
  line.appendChild(document.createTextNode("Shared by "));
  var who = document.createElement("strong");
  who.textContent = name;
  line.appendChild(who);
  wrap.insertBefore(line, wrap.firstChild);
})();
