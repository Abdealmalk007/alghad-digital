"use strict";
/* Alghad Digital v3.1 — accessible contact tools and navigation polish. */
(() => {
  const email = "protech.2025.2026@gmail.com";
  const copyButton = document.getElementById("copy-protech-email");
  const copyMessage = document.getElementById("contact-copy-note");
  const progress = document.getElementById("page-progress");
  const links = [...document.querySelectorAll(".nav a[href^='#']")];
  const toast = document.getElementById("contact-email-toast");
  let toastTimer = null;

  function notify(message) {
    if (copyMessage) copyMessage.textContent = message;
    if (toast) {
      toast.textContent = message;
      toast.hidden = false;
      if (toastTimer !== null) clearTimeout(toastTimer);
      toastTimer = setTimeout(() => { toast.hidden = true; toastTimer = null; }, 2800);
    }
  }

  async function copyEmail() {
    let success = false;
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
      try {
        await navigator.clipboard.writeText(email);
        success = true;
      } catch (_) { /* Fallback to local selection. */ }
    }
    if (!success) {
      const field = document.createElement("textarea");
      field.value = email;
      field.setAttribute("readonly", "");
      field.style.cssText = "position:fixed;left:-9999px;top:0;opacity:0";
      document.body.appendChild(field);
      field.select();
      try { success = document.execCommand("copy"); } catch (_) { success = false; }
      field.remove();
    }
    if (success) {
      notify("تم نسخ بريد ProTech بنجاح");
      if (copyButton) copyButton.textContent = "✓ تم النسخ";
    } else {
      notify("تعذر النسخ تلقائيًا. يمكنك تحديد البريد ونسخه.");
    }
  }

  if (copyButton) copyButton.addEventListener("click", copyEmail);
  if (toast) {
    toast.addEventListener("click", () => { toast.hidden = true; });
    toast.hidden = true;
  }

  // Throttled, non-blocking document progress indicator.
  if (progress) {
    let scheduled = false;
    const update = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const fraction = max > 0 ? Math.min(1,Math.max(0, window.scrollY / max)) : 0;
      progress.style.transform = "scaleX(" + fraction.toFixed(4) + ")";
      scheduled = false;
    };
    const schedule = () => {
      if (!scheduled) {
        scheduled = true;
        requestAnimationFrame(update);
      }
    };
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule, { passive: true });
    schedule();
  }

  // Reflect the visible section in the navigation, including the contact section.
  if (links.length && typeof IntersectionObserver === "function") {
    const ids = new Map();
    links.forEach(link => {
      const id = link.hash.slice(1);
      const section = document.getElementById(id);
      if (section) ids.set(section, link);
    });
    const observer = new IntersectionObserver(entries => {
      const candidates = entries.filter(entry => entry.isIntersecting)
        .sort((a,b) => b.intersectionRatio - a.intersectionRatio);
      if (!candidates.length) return;
      const active = ids.get(candidates[0].target);
      if (!active) return;
      links.forEach(link => {
        if (link === active) link.setAttribute("aria-current", "page");
        else link.removeAttribute("aria-current");
      });
    }, { rootMargin: "-18% 0px -58% 0px", threshold: [0,.05,.3,.65] });
    ids.forEach((_, section) => observer.observe(section));
  }
})();
