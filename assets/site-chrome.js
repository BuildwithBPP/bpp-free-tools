// Adds the buildwithbpp.com top bar + footer to a free-tool page, so every tool
// carries the same chrome as the main site. One source for all pages.
(function () {
  var SITE = "https://www.buildwithbpp.com";
  var MARK = "https://cdn.prod.website-files.com/699f9483b49696115c2aff2c/6a2ad43e91db0ec6e12dc177_bpp-mark-white-2.png";

  var bar = document.createElement("header");
  bar.className = "bpp-bar";
  bar.innerHTML =
    '<nav class="bpp-bar-inner" aria-label="Business Plans Plus">' +
      '<a class="bpp-brand" href="' + SITE + '/"><img src="' + MARK + '" alt="" width="26" height="30">' +
        '<span class="bpp-brand-txt">Business Plans <span class="bpp-accent">Plus</span></span></a>' +
      '<div class="bpp-bar-links">' +
        '<a class="bpp-bar-link" href="' + SITE + '/resources">Free tools</a>' +
        '<a class="bpp-bar-cta" href="' + SITE + '/booking#book">Book a Call</a>' +
      '</div>' +
    '</nav>';

  var footer = document.createElement("footer");
  footer.className = "bpp-footer";
  footer.innerHTML =
    '<div class="bpp-footer-inner"><div class="bpp-footer-grid">' +
      '<div><div class="bpp-footer-brand"><img src="' + MARK + '" alt="" width="31" height="36">Business Plans <span class="bpp-accent">Plus</span></div>' +
        '<p class="bpp-footer-tag">Systems, structure, and AI workflows for businesses that want to run with you, not on you.</p></div>' +
      '<div><div class="bpp-footer-title">Explore</div>' +
        '<a class="bpp-footer-link" href="' + SITE + '/">Home</a>' +
        '<a class="bpp-footer-link" href="' + SITE + '/packages">Packages</a>' +
        '<a class="bpp-footer-link" href="' + SITE + '/about">About</a>' +
        '<a class="bpp-footer-link" href="' + SITE + '/referral">Referral Program</a>' +
        '<a class="bpp-footer-link" href="' + SITE + '/resources">Free Tools</a></div>' +
      '<div><div class="bpp-footer-title">Get started</div>' +
        '<a class="bpp-footer-link" href="' + SITE + '/booking#book">Book a discovery call</a>' +
        '<a class="bpp-footer-link" href="' + SITE + '/booking#book">Contact us</a>' +
        '<span class="bpp-footer-text">Tampa, FL · <a href="tel:+18133147552">(813) 314-7552</a> · <a href="mailto:info@buildwithbpp.com">info@buildwithbpp.com</a></span>' +
        '<a class="bpp-footer-link" href="https://www.google.com/maps?cid=5163829519753823693" target="_blank" rel="noopener noreferrer">Rated 4.9 on Google</a></div>' +
    '</div>' +
    '<div class="bpp-footer-bottom"><span>© ' + new Date().getFullYear() + ' Business Plans Plus. All rights reserved.</span><span>Stop guessing. Start growing.</span></div></div>';

  document.body.insertBefore(bar, document.body.firstChild);
  document.body.appendChild(footer);
})();
