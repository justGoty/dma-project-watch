"use strict";
const projects = {
  "ufrisk/MemProcFS": {name: "MemProcFS", category: "Memory analysis runtime", symbol: "M", color: "#79e3bd", description: "The virtual filesystem and memory analysis layer behind the stack."},
  "ufrisk/LeechCore": {name: "LeechCore", category: "Acquisition transport", symbol: "L", color: "#81b7f5", description: "Memory acquisition library and the transport foundation for DMA reads."},
  "ufrisk/pcileech": {name: "PCILeech", category: "DMA tooling", symbol: "P", color: "#bc9af3", description: "Upstream tooling for PCIe-based memory access and acquisition."},
  "justGoty/goty-esp-dma-tarkov": {name: "GOTY · Tarkov", category: "Public source snapshot", symbol: "G", color: "#e7b881", description: "C++ DMA/ESP source, Fuser rendering and offline runtime-policy checks."},
  "justGoty/dma-project-watch": {name: "DMA Project Watch", category: "DevOps & release intelligence", symbol: "W", color: "#7bd5d8", description: "The CLI, container and automated delivery pipeline powering this dashboard."}
};
let report = null;
const byId = id => document.getElementById(id);
const dateLabel = value => {
  const date = new Date(value);
  return value && Number.isFinite(date.getTime()) ? date.toLocaleDateString("en-GB", {day:"2-digit",month:"short",year:"numeric"}) : "Date unavailable";
};
function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function githubLink(url, text, className) {
  const link = element("a", className, text);
  try {
    const parsed = new URL(url);
    if (parsed.protocol === "https:" && parsed.hostname === "github.com") {
      link.href = parsed.href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
  } catch (_) { /* Invalid external URLs are displayed as text without navigation. */ }
  return link;
}
function renderCard(item) {
  const meta = projects[item.repository] || {name:item.repository,category:"Tracked project",symbol:"+",color:"#79e3bd",description:"Public GitHub release metadata."};
  const card = element("article", "project-card");
  card.style.setProperty("--accent", meta.color);
  const top = element("div", "card-top");
  top.append(element("span", "project-symbol", meta.symbol));
  const identity = element("div");
  identity.append(element("h3", "project-title", meta.name), element("span", "project-category", meta.category));
  top.append(identity, githubLink("https://github.com/" + item.repository, "↗"));
  card.append(top, element("p", "project-description", meta.description));
  const row = element("div", "release-row");
  const found = item.status === "release";
  row.append(element("span", "release-tag", found ? item.tag : item.status === "error" ? "Request failed" : "No release found"));
  row.append(element("span", "release-state" + (found ? "" : item.status === "error" ? " error" : " missing"), found ? "PUBLISHED" : item.status === "error" ? "API ERROR" : "UNAVAILABLE"));
  const details = element("div", "card-meta");
  details.append(element("span", "", found ? dateLabel(item.published_at) : item.message || "Not found or no published release"));
  if (found) details.append(githubLink(item.url, "View release ↗"));
  card.append(row, details);
  return card;
}
function renderProjects() {
  if (!report) return;
  const term = byId("search").value.trim().toLowerCase();
  const status = byId("status-filter").value;
  const filtered = report.repositories.filter(item => (status === "all" || item.status === status) &&
    (item.repository + " " + (projects[item.repository]?.name || "")).toLowerCase().includes(term));
  byId("projects").replaceChildren(...filtered.map(renderCard));
  byId("no-results").hidden = filtered.length > 0;
}
function render() {
  const items = report.repositories;
  const errors = items.filter(item=>item.status === "error").length;
  byId("tool-version").textContent = "v" + report.tool_version;
  byId("total-count").textContent = items.length;
  byId("release-count").textContent = items.filter(item=>item.status === "release").length;
  byId("missing-count").textContent = items.filter(item=>item.status === "not-found-or-no-release").length;
  byId("error-count").textContent = errors;
  const generated = new Date(report.generated_at);
  const age = Date.now() - generated.getTime();
  const stale = !Number.isFinite(age) || age < -300000 || age > 30 * 60 * 60 * 1000;
  byId("data-status").className = "data-status" + (errors ? " error" : stale ? " warning" : "");
  byId("freshness-label").textContent = errors ? "Snapshot contains API errors" : stale ? "Snapshot needs a refresh" : "Snapshot is fresh";
  byId("checked-at").textContent = "Generated " + (Number.isFinite(generated.getTime()) ? generated.toLocaleString("en-GB",{dateStyle:"medium",timeStyle:"short"}) : "at an unknown time");
  renderProjects();
  const releases = items.filter(item=>item.status === "release").sort((a,b)=> (Date.parse(b.published_at)||0)-(Date.parse(a.published_at)||0));
  const timeline = releases.map(item => {
    const row = element("div", "timeline-item");
    const content = element("div");
    content.append(githubLink(item.url, (projects[item.repository]?.name || item.repository) + " · " + item.tag), element("small", "", item.repository));
    row.append(content, element("time", "", dateLabel(item.published_at)));
    return row;
  });
  byId("timeline").replaceChildren(...(timeline.length ? timeline : [element("p", "muted", "No published releases in this snapshot.")]));
}
async function load() {
  byId("refresh").disabled = true;
  try {
    const response = await fetch("snapshot.json", {cache:"no-store"});
    if (!response.ok) throw new Error("Snapshot request failed");
    const data = await response.json();
    if (data.schema_version !== 1 || !Array.isArray(data.repositories) || typeof data.generated_at !== "string" ||
        data.repositories.some(item=>!item || typeof item.repository !== "string" ||
          !["release","error","not-found-or-no-release"].includes(item.status) ||
          (item.status === "release" && (typeof item.tag !== "string" || typeof item.url !== "string")))) throw new Error("Invalid snapshot schema");
    report = data;
    render();
  } catch (_) {
    byId("data-status").className = "data-status error";
    byId("freshness-label").textContent = "Could not load the snapshot";
    byId("checked-at").textContent = report ? "Showing the last loaded data; reload failed" : "Check the deployment or try reloading";
    if (!report) byId("projects").replaceChildren(element("div", "empty-state", "Snapshot unavailable. No status is being guessed."));
  } finally { byId("refresh").disabled = false; }
}
byId("search").addEventListener("input", renderProjects);
byId("status-filter").addEventListener("change", renderProjects);
byId("refresh").addEventListener("click", load);
byId("copy-command").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText("dma-watch --snapshot --json"); byId("copy-feedback").textContent = "Command copied"; }
  catch (_) { byId("copy-feedback").textContent = "Select and copy the command above"; }
});
document.querySelectorAll(".nav-item").forEach(link=>link.addEventListener("click",()=>{
  document.querySelectorAll(".nav-item").forEach(item=>item.classList.remove("active"));
  link.classList.add("active");
}));
load();
