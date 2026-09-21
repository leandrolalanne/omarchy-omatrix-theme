/* Own the live palette and reload it after an Omarchy theme set.
 *
 * The stylesheet is NOT declared in the manifest. It is fetched from
 * active.css on an interval and injected, which means the CSS can change
 * without reloading the extension or the page -- Chromium only reads
 * --load-extension at startup, so a manifest-declared sheet would cost a
 * browser restart per edit.
 *
 * active.css is written by the theme hook: the omatrix stylesheet while that
 * theme is current, an empty file otherwise. So this extension can stay loaded
 * for every theme and paint nothing under the others.
 */
(() => {
  const styleId = "omatrix-whatsapp-live";
  let lastCss = null;

  async function refresh() {
    try {
      const url = `${chrome.runtime.getURL("active.css")}?v=${Date.now()}`;
      const css = await (await fetch(url, { cache: "no-store" })).text();
      if (css === lastCss) return;

      let style = document.getElementById(styleId);
      if (!style) {
        style = document.createElement("style");
        style.id = styleId;
        (document.head || document.documentElement).appendChild(style);
      }
      style.textContent = css;
      lastCss = css;
    } catch (_) {
      /* The page can be mid-navigation; the next tick retries. */
    }
  }

  refresh();
  setInterval(refresh, 2000);
})();
