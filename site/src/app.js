const LANG_KEY = "glyph-site-language";
const LANGS = ["pl", "en"];
const DATA_REFRESH_MS = 5 * 60 * 1000;
const DEMO_PROMPT_LIMIT = 500;

const demoState = {
  prompt: "",
  output: "",
  meta: "",
  error: "",
  loading: false
};

const ui = {
  en: {
    language: "Language",
    modelType: "Model type",
    parameters: "Parameters",
    layers: "Layers",
    heads: "Heads",
    embedding: "Embedding dim",
    ffn: "FFN dim",
    context: "Context length",
    tokenizer: "Tokenizer",
    vocab: "Vocab size",
    framework: "Framework",
    dropout: "Dropout",
    steps: "Training steps",
    progress: "Progress",
    trainLoss: "Train loss",
    validationLoss: "Validation loss",
    tokens: "Tokens processed",
    learningRate: "Learning rate",
    throughput: "Throughput",
    checkpoint: "Checkpoint",
    checkpointStep: "Checkpoint step",
    snapshot: "Snapshot",
    method: "Method",
    promptCount: "Prompt set",
    continuationFit: "Continuation fit",
    polish: "Polish fluency",
    coherence: "Coherence",
    repetition: "Low repetition",
    safety: "Safety",
    category: "Category",
    purpose: "Purpose",
    publicOnly: "Only sanitized public data is shown here.",
    contact: "site owner",
    phase: "Phase",
    dataset: "Dataset",
    split: "Train / val",
    sftTokens: "SFT tokens",
    epoch: "Epoch",
    device: "Device",
    evalStatus: "Eval status",
    evalResult: "Eval result",
    evalPrompts: "Eval prompts",
    evalV2: "Eval v2",
    decoding: "Decoding",
    readiness: "Readiness",
    rocmSmoke: "ROCm smoke",
    trainTokens: "Train tokens",
    valTokens: "Val tokens",
    effectiveBatch: "Effective batch",
    stageStep: "Stage step",
    stageLoss: "Stage loss",
    stageError: "Stop condition"
  },
  pl: {
    language: "Język",
    modelType: "Typ modelu",
    parameters: "Parametry",
    layers: "Warstwy",
    heads: "Głowy",
    embedding: "Wymiar embeddingu",
    ffn: "FFN dim",
    context: "Długość kontekstu",
    tokenizer: "Tokenizer",
    vocab: "Rozmiar vocab",
    framework: "Framework",
    dropout: "Dropout",
    steps: "Kroki treningu",
    progress: "Postęp",
    trainLoss: "Train loss",
    validationLoss: "Validation loss",
    tokens: "Tokeny",
    learningRate: "Learning rate",
    throughput: "Przepustowość",
    checkpoint: "Checkpoint",
    checkpointStep: "Krok checkpointu",
    snapshot: "Snapshot",
    method: "Metoda",
    promptCount: "Zestaw promptów",
    continuationFit: "Dopasowanie kontynuacji",
    polish: "Polszczyzna",
    coherence: "Spójność",
    repetition: "Mała powtarzalność",
    safety: "Bezpieczeństwo",
    category: "Kategoria",
    purpose: "Cel",
    publicOnly: "Tutaj widać tylko oczyszczone dane publiczne.",
    contact: "właściciel strony",
    phase: "Faza",
    dataset: "Dataset",
    split: "Train / val",
    sftTokens: "Tokeny SFT",
    epoch: "Epoka",
    device: "Device",
    evalStatus: "Status eval",
    evalResult: "Wynik eval",
    evalPrompts: "Promptów eval",
    evalV2: "Eval v2",
    decoding: "Decoding",
    readiness: "Gotowość",
    rocmSmoke: "ROCm smoke",
    trainTokens: "Tokeny train",
    valTokens: "Tokeny val",
    effectiveBatch: "Effective batch",
    stageStep: "Krok stage",
    stageLoss: "Stage loss",
    stageError: "Warunek stopu"
  }
};

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

function attr(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}

async function readJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Could not load ${path}: ${response.status}`);
  }
  return response.json();
}

function getInitialLanguage() {
  try {
    const saved = localStorage.getItem(LANG_KEY);
    if (LANGS.includes(saved)) {
      return saved;
    }
  } catch {
    // localStorage can be blocked in hardened browsers.
  }

  const browserLanguages = navigator.languages?.length ? navigator.languages : [navigator.language || "en"];
  const firstLanguage = String(browserLanguages[0] || "en").toLowerCase();
  return firstLanguage.startsWith("pl") ? "pl" : "en";
}

function saveLanguage(lang) {
  try {
    localStorage.setItem(LANG_KEY, lang);
  } catch {
    // Non-critical preference.
  }
}

function setMeta(content, lang) {
  document.documentElement.lang = lang;
  document.title = content.meta.title;
  setMetaTag("description", content.meta.description);
  setPropertyTag("og:title", content.meta.title);
  setPropertyTag("og:description", content.meta.description);
  setPropertyTag("og:locale", lang === "pl" ? "pl_PL" : "en_US");
}

function setMetaTag(name, content) {
  const node = document.querySelector(`meta[name="${name}"]`);
  if (node) node.setAttribute("content", content);
}

function setPropertyTag(property, content) {
  let node = document.querySelector(`meta[property="${property}"]`);
  if (!node) {
    node = document.createElement("meta");
    node.setAttribute("property", property);
    document.head.appendChild(node);
  }
  node.setAttribute("content", content);
}

function metricCard(label, value, detail = "") {
  return `
    <article class="metric-card reveal">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      ${detail ? `<small>${escapeHtml(detail)}</small>` : ""}
    </article>
  `;
}

function specCard(label, value) {
  return `
    <article class="spec-card reveal">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </article>
  `;
}

function progressBar(percent) {
  const safePercent = Math.max(0, Math.min(100, Number(percent) || 0));
  return `
    <div class="progress-track" aria-label="${attr(`${safePercent.toFixed(1)}%`)}">
      <span style="width: ${safePercent.toFixed(3)}%"></span>
    </div>
  `;
}

function renderHeader(content, lang) {
  const nav = content.nav
    .map(([id, label]) => `<a href="#${attr(id)}">${escapeHtml(label)}</a>`)
    .join("");

  return `
    <header class="site-header">
      <div class="header-inner">
        <a class="brand" href="#top" aria-label="Glyph">
          <img src="assets/glyph_mark.png" alt="" width="34" height="48">
          <span>Glyph</span>
        </a>
        <nav class="nav" aria-label="Primary navigation">${nav}</nav>
        <div class="lang-switch" aria-label="${attr(ui[lang].language)}">
          ${LANGS.map((item) => `
            <button type="button" data-lang="${item}" class="${item === lang ? "active" : ""}" aria-pressed="${item === lang}">
              ${item.toUpperCase()}
            </button>
          `).join("")}
        </div>
      </div>
    </header>
  `;
}

function renderHero(content) {
  const author = content.hero.author;
  const authorLine = author ? `
    <p class="hero-author">
      <span>${escapeHtml(author.text)}</span>
      <b aria-hidden="true">·</b>
      <a href="${attr(author.url)}" target="_blank" rel="noreferrer">${escapeHtml(author.linkLabel)}</a>
    </p>
  ` : "";

  return `
    <section id="top" class="hero">
      <div class="section-inner hero-inner">
        <div class="hero-copy reveal">
          <p class="eyebrow">${escapeHtml(content.hero.eyebrow)}</p>
          <h1>${escapeHtml(content.hero.title)}</h1>
          <p class="hero-lead">${escapeHtml(content.hero.lead)}</p>
          <p class="hero-body">${escapeHtml(content.hero.body)}</p>
          ${authorLine}
          <div class="hero-metrics">
            ${content.hero.metrics.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
          </div>
          <div class="hero-ctas">
            ${content.hero.ctas.map(([id, label]) => `<a href="#${attr(id)}">${escapeHtml(label)}</a>`).join("")}
          </div>
        </div>
        <div class="hero-symbol reveal" aria-hidden="true">
          <img src="assets/glyph_mark.png" alt="">
        </div>
      </div>
    </section>
  `;
}

function renderSpecs(content, model, lang) {
  const t = ui[lang];
  const specs = [
    [t.modelType, model.type],
    [t.parameters, `~${model.parameters.display}`],
    [t.layers, model.architecture.layers],
    [t.heads, model.architecture.heads],
    [t.embedding, model.architecture.embeddingDim],
    [t.ffn, model.architecture.ffnDim],
    [t.context, model.architecture.contextLength],
    [t.tokenizer, model.tokenizer.type],
    [t.vocab, model.tokenizer.vocabSize.toLocaleString(lang === "pl" ? "pl-PL" : "en-US")],
    [t.framework, model.framework],
    [t.dropout, model.architecture.dropout]
  ];

  return `
    <section id="model-card" class="section">
      <div class="section-inner split">
        <div class="section-copy reveal">
          <p class="eyebrow">${escapeHtml(content.sections.specs.kicker)}</p>
          <h2>${escapeHtml(content.sections.specs.title)}</h2>
          <p>${escapeHtml(content.sections.specs.body)}</p>
        </div>
        <div class="diagram reveal" aria-label="Model pipeline">
          ${content.sections.specs.diagram.map((item, index) => `
            <span>${escapeHtml(item)}</span>
            ${index < content.sections.specs.diagram.length - 1 ? "<b>→</b>" : ""}
          `).join("")}
        </div>
      </div>
      <div class="section-inner">
        <div class="spec-grid">${specs.map(([label, value]) => specCard(label, value)).join("")}</div>
      </div>
    </section>
  `;
}

function renderWhy(content) {
  return `
    <section id="why" class="section quiet">
      <div class="section-inner narrow reveal">
        <p class="eyebrow">${escapeHtml(content.sections.why.kicker)}</p>
        <h2>${escapeHtml(content.sections.why.title)}</h2>
        <p>${escapeHtml(content.sections.why.body)}</p>
      </div>
    </section>
  `;
}

function renderDemo(content) {
  const demo = content.sections.demo;
  const count = Math.min(DEMO_PROMPT_LIMIT, demoState.prompt.length);
  const output = demoState.output || demo.emptyOutput;
  const meta = demoState.meta || demo.limits;
  const buttonLabel = demoState.loading ? demo.generating : demo.generate;

  return `
    <section id="demo" class="section demo-section">
      <div class="section-inner split">
        <div class="section-copy reveal">
          <p class="eyebrow">${escapeHtml(demo.kicker)}</p>
          <h2>${escapeHtml(demo.title)}</h2>
          <p>${escapeHtml(demo.body)}</p>
          <p class="demo-disclaimer">${escapeHtml(demo.disclaimer)}</p>
        </div>
        <form class="demo-panel reveal" id="demo-form">
          <label class="demo-label" for="demo-prompt">
            <span>${escapeHtml(demo.promptLabel)}</span>
            <small id="demo-count">${escapeHtml(`${count}/${DEMO_PROMPT_LIMIT}`)}</small>
          </label>
          <textarea id="demo-prompt" name="prompt" maxlength="${DEMO_PROMPT_LIMIT}" placeholder="${attr(demo.placeholder)}">${escapeHtml(demoState.prompt)}</textarea>
          <div class="demo-examples" aria-label="${attr(demo.examplesLabel)}">
            ${demo.examples.map((prompt) => `<button type="button" data-demo-prompt="${attr(prompt)}">${escapeHtml(prompt)}</button>`).join("")}
          </div>
          <button class="demo-submit" type="submit" ${demoState.loading ? "disabled" : ""}>${escapeHtml(buttonLabel)}</button>
          <div class="demo-output-wrap">
            <div class="demo-output-head">
              <span>${escapeHtml(demo.outputLabel)}</span>
              <small id="demo-meta">${escapeHtml(meta)}</small>
            </div>
            <pre id="demo-output" class="${demoState.output ? "" : "empty"}">${escapeHtml(output)}</pre>
          </div>
          <p class="demo-error" id="demo-error">${escapeHtml(demoState.error)}</p>
          <p class="demo-privacy">${escapeHtml(demo.privacy)}</p>
        </form>
      </div>
    </section>
  `;
}

function renderTraining(content, training, lang) {
  const t = ui[lang];
  const steps = `${Number(training.step).toLocaleString(lang === "pl" ? "pl-PL" : "en-US")} / ${Number(training.totalSteps).toLocaleString(lang === "pl" ? "pl-PL" : "en-US")}`;
  const sft = training.sft;
  const sftEval = sft?.evaluation;
  const sftV2 = sftEval?.v2;
  const sweep = sftEval?.decodingSweep;
  const sftEvalPanel = sftEval ? `
            <p class="note">${escapeHtml(content.sections.training.sftEvalNote || sftEval.verdict || "")}</p>
            <div class="metric-grid compact">
              ${metricCard(t.evalStatus, sftEval.status)}
              ${metricCard(t.evalPrompts, String(sftEval.promptCount))}
              ${metricCard(t.evalResult, sftEval.summary)}
              ${sftV2 ? metricCard(t.evalV2, sftV2.summary, sftV2.weakSftWinsRemoved != null ? `${sftV2.weakSftWinsRemoved} weak SFT wins removed` : "") : ""}
              ${sweep ? metricCard(t.decoding, sweep.recommendedDemoPreset || "pending", sweep.status) : ""}
            </div>
  ` : "";
  const sftPanel = sft ? `
          <div class="training-subpanel">
            <div class="training-topline">
              <span>${escapeHtml(content.sections.training.sftTitle || "SFT v0")}</span>
              <strong>${escapeHtml(sft.status)}</strong>
            </div>
            <p class="note">${escapeHtml(content.sections.training.sftBody || "")}</p>
            <div class="metric-grid compact">
              ${metricCard(t.phase, sft.phase)}
              ${metricCard(t.dataset, sft.dataset)}
              ${metricCard(t.split, sft.split)}
              ${metricCard(t.sftTokens, sft.tokens)}
              ${metricCard(t.steps, String(sft.step))}
              ${metricCard(t.epoch, String(sft.epoch))}
              ${metricCard(t.trainLoss, sft.trainLoss)}
              ${metricCard(t.validationLoss, sft.validationLoss)}
              ${metricCard(t.device, sft.device)}
              ${metricCard(t.checkpoint, sft.checkpoint)}
            </div>
            ${sftEvalPanel}
          </div>
  ` : "";
  const glyph100 = training.glyph100;
  const glyph100Stage = glyph100?.stage || {};
  const glyph100Panel = glyph100 ? `
          <div class="training-subpanel">
            <div class="training-topline">
              <span>${escapeHtml(content.sections.training.glyph100Title || "Glyph-100M")}</span>
              <strong>${escapeHtml(glyph100.status)}</strong>
            </div>
            <p class="note">${escapeHtml(content.sections.training.glyph100Body || glyph100.notes || "")}</p>
            <div class="metric-grid compact">
              ${metricCard(t.parameters, glyph100.parameters)}
              ${metricCard(t.context, glyph100.context)}
              ${metricCard(t.dataset, glyph100.dataset)}
              ${metricCard(t.trainTokens, glyph100.trainTokens)}
              ${metricCard(t.valTokens, glyph100.valTokens)}
              ${metricCard(t.device, glyph100.device)}
              ${metricCard(t.rocmSmoke, glyph100.rocmSmoke)}
              ${metricCard(t.effectiveBatch, glyph100.effectiveBatch)}
              ${metricCard(t.stageStep, `${glyph100Stage.step ?? 0} / ${glyph100Stage.totalSteps ?? 10000}`)}
              ${metricCard(t.stageLoss, glyph100Stage.loss == null ? "not found" : String(glyph100Stage.loss))}
              ${glyph100Stage.error ? metricCard(t.stageError, glyph100Stage.error.reason || "stopped", `step ${glyph100Stage.error.step ?? "?"}`) : ""}
              ${metricCard(t.readiness, glyph100.readiness)}
            </div>
          </div>
  ` : "";
  return `
    <section id="training" class="section">
      <div class="section-inner section-head reveal">
        <p class="eyebrow">${escapeHtml(content.sections.training.kicker)}</p>
        <h2>${escapeHtml(content.sections.training.title)}</h2>
        <p>${escapeHtml(content.sections.training.body)}</p>
      </div>
      <div class="section-inner">
        <div class="training-panel reveal">
          <div class="training-topline">
            <span>${escapeHtml(content.labels.publicSnapshot)} · ${escapeHtml(training.snapshotDate)}</span>
            <strong>${escapeHtml(training.status)}</strong>
          </div>
          ${progressBar(training.progressPct)}
          <div class="metric-grid">
            ${metricCard(t.steps, steps)}
            ${metricCard(t.progress, `${Number(training.progressPct).toFixed(2)}%`)}
            ${metricCard(t.trainLoss, training.trainLoss)}
            ${metricCard(t.validationLoss, training.validationLoss)}
            ${metricCard(t.tokens, training.tokensProcessed)}
            ${metricCard(t.learningRate, training.learningRate)}
            ${metricCard(t.throughput, training.throughput)}
            ${metricCard(t.checkpoint, training.checkpoint)}
          </div>
          ${sftPanel}
          ${glyph100Panel}
          <p class="note">${escapeHtml(ui[lang].publicOnly)} ${escapeHtml(training.notes)}</p>
        </div>
      </div>
    </section>
  `;
}

function renderDataset(content) {
  return `
    <section id="dataset" class="section quiet">
      <div class="section-inner section-head reveal">
        <p class="eyebrow">${escapeHtml(content.sections.dataset.kicker)}</p>
        <h2>${escapeHtml(content.sections.dataset.title)}</h2>
        <p>${escapeHtml(content.sections.dataset.body)}</p>
      </div>
      <div class="section-inner source-grid">
        ${content.sections.dataset.sources.map(([title, body]) => `
          <article class="source-card reveal">
            <h3>${escapeHtml(title)}</h3>
            <p>${escapeHtml(body)}</p>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderEvaluation(content, evaluation, lang) {
  const t = ui[lang];
  const metricLabels = {
    continuationFit: t.continuationFit,
    polish: t.polish,
    coherence: t.coherence,
    repetition: t.repetition,
    safety: t.safety
  };
  const metricRows = Object.entries(evaluation.metrics || {}).filter(([, value]) => Number.isFinite(Number(value))).map(([key, value]) => {
    const width = Math.max(0, Math.min(100, (Number(value) / 5) * 100));
    return `
      <div class="score-row">
        <span>${escapeHtml(metricLabels[key] || key)}</span>
        <div class="score-track"><i style="width: ${width.toFixed(2)}%"></i></div>
        <strong>${escapeHtml(Number(value).toFixed(2))}</strong>
      </div>
    `;
  }).join("");
  const overall = Number.isFinite(Number(evaluation.overall)) ? Number(evaluation.overall).toFixed(2) : "—";
  const promptCount = `${evaluation.validCount ?? 0}/${evaluation.count ?? 0}`;

  return `
    <section id="evaluation" class="section">
      <div class="section-inner split">
        <div class="section-copy reveal">
          <p class="eyebrow">${escapeHtml(content.sections.evaluation.kicker)}</p>
          <h2>${escapeHtml(content.sections.evaluation.title)}</h2>
          <p>${escapeHtml(content.sections.evaluation.body)}</p>
          <div class="eval-meta">
            <span>${escapeHtml(t.method)}: ${escapeHtml(evaluation.method)}</span>
            <span>${escapeHtml(t.promptCount)}: ${escapeHtml(promptCount)}</span>
            <span>${escapeHtml(t.snapshot)}: ${escapeHtml(evaluation.snapshotDate || "—")}</span>
            <span>${escapeHtml(t.checkpointStep)}: ${escapeHtml(evaluation.checkpointStep || "—")}</span>
          </div>
        </div>
        <div class="score-panel reveal">
          <div class="overall-score">
            <span>${escapeHtml(content.labels.overall)}</span>
            <strong>${escapeHtml(overall)}<small>/5</small></strong>
          </div>
          ${metricRows}
          ${evaluation.description ? `<p class="eval-diagnostic">${escapeHtml(evaluation.description)}</p>` : ""}
        </div>
      </div>
      <div class="section-inner">
        <div class="failure-strip reveal">
          <strong>${escapeHtml(content.sections.evaluation.failureTitle)}</strong>
          <div>
            ${evaluation.failureModes.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderSamples(content, samples, lang) {
  return `
    <section id="samples" class="section quiet">
      <div class="section-inner section-head reveal">
        <p class="eyebrow">${escapeHtml(content.sections.samples.kicker)}</p>
        <h2>${escapeHtml(content.sections.samples.title)}</h2>
        <p>${escapeHtml(content.sections.samples.body)}</p>
      </div>
      <div class="section-inner sample-grid">
        ${samples.map((sample) => renderSampleCard(content, sample, lang)).join("")}
      </div>
    </section>
  `;
}

function renderSampleCard(content, sample, lang) {
  const kindLabel = content.labels[sample.kind] || sample.kind;
  const settings = sample.settings || {};
  const tokenLabel = settings.maxTokens ? `${settings.maxTokens} tokens` : "tokens n/a";
  const settingsLabel = `temp ${settings.temperature ?? "—"} · top-k ${settings.topK ?? "—"} · top-p ${settings.topP ?? "—"} · rep ${settings.repetitionPenalty ?? "—"} · ${tokenLabel}`;
  const comment = sample.comment?.[lang] || sample.comment?.en || "";
  const overall = Number.isFinite(Number(sample.scores?.overall)) ? Number(sample.scores.overall).toFixed(1) : "—";

  return `
    <article class="sample-card ${attr(sample.kind)} reveal">
      <header>
        <span>${escapeHtml(kindLabel)}</span>
        <strong>${escapeHtml(content.labels.score)} ${escapeHtml(overall)}/5</strong>
      </header>
      <dl class="sample-meta">
        <div><dt>${escapeHtml(content.labels.step)}</dt><dd>${escapeHtml(sample.step)}</dd></div>
        <div><dt>${escapeHtml(ui[lang].category)}</dt><dd>${escapeHtml(sample.category)}</dd></div>
      </dl>
      <div class="sample-block">
        <p>${escapeHtml(content.labels.prompt)}</p>
        <blockquote>${escapeHtml(sample.prompt)}</blockquote>
      </div>
      <div class="sample-block">
        <p>${escapeHtml(content.labels.output)}</p>
        <blockquote>${escapeHtml(sample.output)}</blockquote>
      </div>
      <div class="judge-note">
        <p>${escapeHtml(content.labels.judge)}</p>
        <span>${escapeHtml(comment)}</span>
      </div>
      <footer>${escapeHtml(content.labels.settings)}: <span>${escapeHtml(settingsLabel)}</span></footer>
    </article>
  `;
}

function renderLimitations(content) {
  return `
    <section id="limitations" class="section">
      <div class="section-inner section-head reveal">
        <p class="eyebrow">${escapeHtml(content.sections.limitations.kicker)}</p>
        <h2>${escapeHtml(content.sections.limitations.title)}</h2>
        <p>${escapeHtml(content.sections.limitations.body)}</p>
      </div>
      <div class="section-inner limitation-list reveal">
        ${content.sections.limitations.items.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
      </div>
    </section>
  `;
}

function renderRoadmap(content) {
  return `
    <section id="roadmap" class="section quiet">
      <div class="section-inner section-head reveal">
        <p class="eyebrow">${escapeHtml(content.sections.roadmap.kicker)}</p>
        <h2>${escapeHtml(content.sections.roadmap.title)}</h2>
      </div>
      <div class="section-inner roadmap-grid">
        ${content.sections.roadmap.groups.map(([title, items]) => `
          <article class="roadmap-card reveal">
            <h3>${escapeHtml(title)}</h3>
            <ul>
              ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
            </ul>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderFooter(content, lang) {
  const authorUrl = content.hero.author?.url || "https://www.maksu.online";
  return `
    <footer class="site-footer">
      <div class="section-inner footer-inner">
        <div>
          <img src="assets/glyph_mark.png" alt="" width="28" height="40">
          <span>${escapeHtml(content.labels.footer)}</span>
        </div>
        <nav aria-label="Footer">
          <a href="#model-card">${escapeHtml(content.labels.modelCard)}</a>
          <a href="#training">${escapeHtml(content.hero.ctas[3][1])}</a>
          <a href="#samples">${escapeHtml(content.hero.ctas[1][1])}</a>
          <a href="#evaluation">${escapeHtml(content.hero.ctas[2][1])}</a>
          <a href="${attr(authorUrl)}" target="_blank" rel="noreferrer">${escapeHtml(ui[lang].contact)}</a>
        </nav>
      </div>
    </footer>
  `;
}

function activateReveals() {
  const nodes = [...document.querySelectorAll(".reveal")];
  if (!("IntersectionObserver" in window)) {
    nodes.forEach((node) => node.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  nodes.forEach((node) => observer.observe(node));
}

function wireLanguageButtons(currentLang, render) {
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextLang = button.getAttribute("data-lang");
      if (LANGS.includes(nextLang) && nextLang !== currentLang) {
        saveLanguage(nextLang);
        activeLanguage = nextLang;
        render(nextLang);
      }
    });
  });
}

function wireDemo(content) {
  const demo = content.sections.demo;
  const form = document.getElementById("demo-form");
  const textarea = document.getElementById("demo-prompt");
  const count = document.getElementById("demo-count");
  const output = document.getElementById("demo-output");
  const meta = document.getElementById("demo-meta");
  const error = document.getElementById("demo-error");
  if (!form || !textarea || !count || !output || !meta || !error) return;

  const setPrompt = (value) => {
    demoState.prompt = String(value || "").slice(0, DEMO_PROMPT_LIMIT);
    textarea.value = demoState.prompt;
    count.textContent = `${demoState.prompt.length}/${DEMO_PROMPT_LIMIT}`;
  };

  textarea.addEventListener("input", () => {
    demoState.prompt = textarea.value.slice(0, DEMO_PROMPT_LIMIT);
    count.textContent = `${demoState.prompt.length}/${DEMO_PROMPT_LIMIT}`;
  });

  document.querySelectorAll("[data-demo-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
      setPrompt(button.getAttribute("data-demo-prompt") || "");
      textarea.focus();
    });
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const prompt = textarea.value.trim();
    if (!prompt) {
      demoState.error = demo.errors.invalid_prompt;
      error.textContent = demoState.error;
      return;
    }

    demoState.prompt = prompt.slice(0, DEMO_PROMPT_LIMIT);
    demoState.loading = true;
    demoState.error = "";
    error.textContent = "";
    output.textContent = demo.generating;
    output.classList.add("empty");
    meta.textContent = demo.limits;

    const submit = form.querySelector(".demo-submit");
    if (submit) {
      submit.disabled = true;
      submit.textContent = demo.generating;
    }

    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 70000);
    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({ prompt: demoState.prompt }),
        signal: controller.signal
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        const key = payload.error || "internal_error";
        throw new Error(demo.errors[key] || payload.message || demo.errors.internal_error);
      }
      demoState.output = payload.output || "";
      demoState.meta = `${payload.model || "Glyph-27M"} · ${payload.preset || "balanced-long"} · ${Math.round((payload.duration_ms || 0) / 1000)}s`;
      output.textContent = demoState.output;
      output.classList.toggle("empty", !demoState.output);
      meta.textContent = demoState.meta;
    } catch (err) {
      demoState.error = err.name === "AbortError" ? demo.errors.timeout : err.message;
      error.textContent = demoState.error;
      output.textContent = demoState.output || demo.emptyOutput;
      output.classList.toggle("empty", !demoState.output);
    } finally {
      window.clearTimeout(timer);
      demoState.loading = false;
      if (submit) {
        submit.disabled = false;
        submit.textContent = demo.generate;
      }
    }
  });
}

async function loadContent(lang) {
  const [content, model, training, evaluation, samples] = await Promise.all([
    readJson(`content/${lang}.json`),
    readJson("data/model.json"),
    readJson("data/training.json"),
    readJson("data/evaluation.json"),
    readJson("data/samples.json")
  ]);
  return { content, model, training, evaluation, samples };
}

async function render(lang, options = {}) {
  const safeLang = LANGS.includes(lang) ? lang : "en";
  activeLanguage = safeLang;
  const scrollY = options.preserveScroll ? window.scrollY : null;
  const { content, model, training, evaluation, samples } = await loadContent(safeLang);
  setMeta(content, safeLang);

  const app = document.getElementById("app");
  app.innerHTML = `
    ${renderHeader(content, safeLang)}
    <main>
      ${renderHero(content, model)}
      ${renderSpecs(content, model, safeLang)}
      ${renderWhy(content)}
      ${renderDemo(content)}
      ${renderTraining(content, training, safeLang)}
      ${renderDataset(content)}
      ${renderEvaluation(content, evaluation, safeLang)}
      ${renderSamples(content, samples, safeLang)}
      ${renderLimitations(content)}
      ${renderRoadmap(content)}
    </main>
    ${renderFooter(content, safeLang)}
  `;

  wireLanguageButtons(safeLang, render);
  wireDemo(content);
  activateReveals();
  if (scrollY !== null) {
    requestAnimationFrame(() => window.scrollTo({ top: scrollY, left: 0, behavior: "auto" }));
  }
}

let activeLanguage = getInitialLanguage();
let refreshTimer = null;

function scheduleDataRefresh() {
  if (refreshTimer) {
    window.clearInterval(refreshTimer);
  }
  refreshTimer = window.setInterval(() => {
    render(activeLanguage, { preserveScroll: true }).catch((error) => console.error(error));
  }, DATA_REFRESH_MS);

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
      render(activeLanguage, { preserveScroll: true }).catch((error) => console.error(error));
    }
  });
}

render(activeLanguage).then(scheduleDataRefresh).catch((error) => {
  console.error(error);
  document.getElementById("app").innerHTML = `
    <main class="boot error">
      <img src="assets/glyph_mark.png" alt="" width="76" height="76">
      <h1>Glyph-27M</h1>
      <p>Could not load the public project page data.</p>
    </main>
  `;
});
