"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.resolve(__dirname, "../assets/analytics-consent.js"), "utf8");
const measurementId = "G-TEST123456";

function element(tagName) {
  return {
    tagName,
    className: "",
    textContent: "",
    children: [],
    listeners: new Map(),
    attributes: {},
    appendChild(child) { this.children.push(child); child.parent = this; return child; },
    append(...children) { for (const child of children) this.appendChild(child); },
    setAttribute(key, value) { this.attributes[key] = value; },
    addEventListener(type, callback) { this.listeners.set(type, callback); },
    remove() { if (this.parent) this.parent.children = this.parent.children.filter(x => x !== this); },
    click() { assert.ok(this.listeners.has("click"), "Clickable element missing handler"); this.listeners.get("click")(); },
  };
}
function findNode(root, predicate) {
  if (predicate(root)) return root;
  for (const child of root.children) {
    const match = findNode(child, predicate);
    if (match) return match;
  }
  return null;
}
function makePage({ consent = null, storageBlocked = false, lang = "ar", id = measurementId } = {}) {
  const state = { consent, reloads: 0, cookieWrites: [] };
  const head = element("head");
  const body = element("body");
  const footer = element("footer");
  body.appendChild(footer);
  const document = {
    head, body, readyState: "complete", documentElement: { lang },
    createElement(name) { return element(name); },
    getElementById(name) {
      return name === "protech-analytics"
        ? { getAttribute(attr) { return attr === "data-ga4-id" ? id : null; } }
        : null;
    },
    querySelector(selector) {
      if (selector === "footer") return footer;
      if (selector === ".site-footer .shell") return null;
      if (selector === ".protech-analytics-consent") {
        return findNode(body, node => node.className === "protech-analytics-consent");
      }
      return null;
    },
  };
  Object.defineProperty(document, "cookie", {
    get() { return "_ga=oldvalue; _ga_TEST=other; session=keep"; },
    set(value) { state.cookieWrites.push(value); },
  });
  const storage = {
    getItem(key) { assert.equal(key, "alghad_analytics_consent_v1"); if (storageBlocked) throw Error("Storage denied"); return state.consent; },
    setItem(key, value) { assert.equal(key, "alghad_analytics_consent_v1"); if (storageBlocked) throw Error("Storage denied"); state.consent = value; },
  };
  const win = {};
  vm.runInNewContext(source, {
    document,
    window: win,
    localStorage: storage,
    location: { reload() { state.reloads++; } },
    encodeURIComponent,
    Date,
  }, { filename: "assets/analytics-consent.js", timeout: 1500 });
  const find = className => findNode(body, node => node.className === className);
  const button = className => {
    const match = findNode(body, node => node.className.includes(className));
    assert.ok(match, "Missing button " + className);
    return match;
  };
  return {
    state, document, win, find, button, scripts() {
      return head.children.filter(node => node.tagName === "script");
    },
  };
}

// No analytics request before explicit consent.
const fresh = makePage();
assert.equal(fresh.scripts().length, 0);
assert.ok(fresh.find("protech-analytics-consent"));
assert.equal(fresh.button("protech-analytics-choice decline").textContent, "لا أوافق");
fresh.button("protech-analytics-choice accept").click();
assert.equal(fresh.state.consent, "yes");
assert.equal(fresh.scripts().length, 1);
assert.equal(fresh.scripts()[0].src, "https://www.googletagmanager.com/gtag/js?id=" + measurementId);
assert.equal(fresh.win.dataLayer.length, 2);

// A previously accepted visitor loads one tag, and can revoke consent.
const returning = makePage({ consent: "yes", lang: "en" });
assert.equal(returning.scripts().length, 1);
returning.button("protech-analytics-preferences").click();
assert.equal(returning.button("protech-analytics-choice decline").textContent, "Decline");
returning.button("protech-analytics-choice decline").click();
assert.equal(returning.state.consent, "no");
assert.equal(returning.state.reloads, 1);
assert.ok(returning.state.cookieWrites.some(value => value.includes("_ga=")));

// A rejected visitor never loads Google scripts, but can later opt in.
const rejected = makePage({ consent: "no" });
assert.equal(rejected.scripts().length, 0);
assert.equal(rejected.find("protech-analytics-consent"), null);
rejected.button("protech-analytics-preferences").click();
rejected.button("protech-analytics-choice accept").click();
assert.equal(rejected.scripts().length, 1);

// A first-time decline must not trigger any Google request.
const declined = makePage();
declined.button("protech-analytics-choice decline").click();
assert.equal(declined.state.consent, "no");
assert.equal(declined.scripts().length, 0);
assert.equal(declined.state.reloads, 0);

// Privacy must remain revocable when storage APIs are blocked by browser policy.
const restricted = makePage({ storageBlocked: true });
restricted.button("protech-analytics-choice accept").click();
assert.equal(restricted.scripts().length, 1);
restricted.button("protech-analytics-preferences").click();
restricted.button("protech-analytics-choice decline").click();
assert.equal(restricted.state.reloads, 1, "Revocation must reload even without localStorage");
assert.ok(restricted.state.cookieWrites.length > 0);

// A missing or invalid GA4 identifier must not initialize analytics.
const invalid = makePage({ id: "not-a-measurement-id" });
assert.equal(invalid.scripts().length, 0);
assert.equal(invalid.find("protech-analytics-consent"), null);

console.log("ANALYTICS_CONSENT_RUNTIME_PASS", {
  scenarios: 6,
  storageBlockedRevocation: true,
  noPreConsentRequests: true,
});
