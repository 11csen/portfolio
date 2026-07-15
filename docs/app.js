/*
 * Protein of the Day — client-side app.
 *
 * The selection algorithm is the exact twin of the Python implementation in
 * src/protein_of_the_day/selector.py:
 *
 *     epochDay = whole days between 1970-01-01 and the (local) calendar date
 *     index    = epochDay mod (number of proteins)
 *
 * Using Date.UTC on the local Y/M/D keeps the arithmetic a pure calendar-day
 * count, independent of the viewer's time zone, so it matches Python's
 * date.toordinal()-style maths day for day.
 */
(function () {
  "use strict";

  var MS_PER_DAY = 86400000;
  var state = { proteins: [], date: startOfToday() };

  var els = {
    app: document.getElementById("app"),
    status: document.getElementById("status"),
    picker: document.getElementById("date-picker"),
    prev: document.getElementById("prev"),
    next: document.getElementById("next"),
    today: document.getElementById("today"),
    template: document.getElementById("card-template"),
  };

  function startOfToday() {
    var now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate());
  }

  function epochDay(date) {
    return Math.floor(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) / MS_PER_DAY);
  }

  function indexForDate(date, count) {
    return ((epochDay(date) % count) + count) % count;
  }

  function proteinForDate(date) {
    if (!state.proteins.length) return null;
    return state.proteins[indexForDate(date, state.proteins.length)];
  }

  function isoDate(date) {
    var y = date.getFullYear();
    var m = String(date.getMonth() + 1).padStart(2, "0");
    var d = String(date.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + d;
  }

  function prettyDate(date) {
    try {
      return date.toLocaleDateString(undefined, {
        weekday: "long", year: "numeric", month: "long", day: "numeric",
      });
    } catch (err) {
      return isoDate(date);
    }
  }

  function addDays(date, delta) {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate() + delta);
  }

  function metaRow(term, value) {
    var row = document.createElement("div");
    row.className = "meta-row";
    var dt = document.createElement("dt");
    dt.textContent = term;
    var dd = document.createElement("dd");
    if (value instanceof Node) {
      dd.appendChild(value);
    } else {
      dd.textContent = value;
    }
    row.appendChild(dt);
    row.appendChild(dd);
    return row;
  }

  function rcsbStructureUrl(pdbId) {
    return "https://www.rcsb.org/structure/" + encodeURIComponent(pdbId);
  }

  function rcsb3dUrl(pdbId) {
    return "https://www.rcsb.org/3d-view/" + encodeURIComponent(pdbId);
  }

  function rcsbImageUrl(pdbId) {
    return "https://cdn.rcsb.org/images/structures/" + pdbId.toLowerCase() + "_assembly-1.jpeg";
  }

  function render(date) {
    var protein = proteinForDate(date);
    if (!protein) return;

    var fragment = els.template.content.cloneNode(true);
    var card = fragment.querySelector(".card");

    var img = fragment.querySelector(".card-image");
    var fallback = fragment.querySelector(".card-image-fallback");
    img.src = rcsbImageUrl(protein.pdb_id);
    img.alt = "Structure of " + protein.name + " (PDB " + protein.pdb_id + ")";
    img.addEventListener("error", function () {
      img.hidden = true;
      fallback.hidden = false;
    });

    fragment.querySelector(".card-date").textContent =
      "Protein of the Day · " + prettyDate(date);
    fragment.querySelector(".card-name").textContent = protein.name;
    fragment.querySelector(".card-tagline").textContent = "“" + protein.tagline + "”";

    var meta = fragment.querySelector(".card-meta");
    meta.appendChild(metaRow("Category", protein.category));
    meta.appendChild(metaRow("Organism", protein.organism));
    var pdbLink = document.createElement("a");
    pdbLink.href = rcsbStructureUrl(protein.pdb_id);
    pdbLink.target = "_blank";
    pdbLink.rel = "noopener";
    pdbLink.textContent = protein.pdb_id;
    meta.appendChild(metaRow("PDB entry", pdbLink));

    fragment.querySelector(".card-description").textContent = protein.description;

    var fun = fragment.querySelector(".card-fun-fact");
    var funLabel = document.createElement("strong");
    funLabel.textContent = "Did you know? ";
    fun.appendChild(funLabel);
    fun.appendChild(document.createTextNode(protein.fun_fact));

    var rcsb = fragment.querySelector(".link-rcsb");
    rcsb.href = rcsbStructureUrl(protein.pdb_id);
    var view3d = fragment.querySelector(".link-3d");
    view3d.href = rcsb3dUrl(protein.pdb_id);

    els.app.innerHTML = "";
    els.app.appendChild(fragment);
    els.picker.value = isoDate(date);
    document.title = protein.name + " · Protein of the Day";

    enrichFromRcsb(protein, card);
  }

  /*
   * Best-effort live enrichment. If the RCSB API is reachable and permits
   * cross-origin requests, we append a couple of extra facts. Any failure is
   * silently ignored — the offline card is always complete on its own.
   */
  function enrichFromRcsb(protein, card) {
    var url = "https://data.rcsb.org/rest/v1/core/entry/" + encodeURIComponent(protein.pdb_id.toUpperCase());
    fetch(url, { headers: { Accept: "application/json" } })
      .then(function (resp) { return resp.ok ? resp.json() : null; })
      .then(function (data) {
        if (!data || card !== els.app.querySelector(".card")) return;
        var meta = card.querySelector(".card-meta");
        if (!meta) return;
        var res = data.rcsb_entry_info && data.rcsb_entry_info.resolution_combined;
        if (res && res.length) {
          meta.appendChild(metaRow("Resolution", res[0].toFixed(2) + " Å"));
        }
        var release = data.rcsb_accession_info && data.rcsb_accession_info.initial_release_date;
        if (release) {
          meta.appendChild(metaRow("Released", String(release).slice(0, 10)));
        }
      })
      .catch(function () { /* offline or blocked — ignore */ });
  }

  function showError(message) {
    els.status.textContent = message;
    els.status.className = "status error";
  }

  function goto(date) {
    state.date = date;
    render(date);
  }

  function wireEvents() {
    els.prev.addEventListener("click", function () { goto(addDays(state.date, -1)); });
    els.next.addEventListener("click", function () { goto(addDays(state.date, 1)); });
    els.today.addEventListener("click", function () { goto(startOfToday()); });
    els.picker.addEventListener("change", function () {
      var parts = els.picker.value.split("-");
      if (parts.length === 3) {
        goto(new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])));
      }
    });
  }

  fetch("proteins.json")
    .then(function (resp) {
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      return resp.json();
    })
    .then(function (data) {
      var list = Array.isArray(data) ? data : data.proteins;
      if (!list || !list.length) throw new Error("empty catalogue");
      state.proteins = list;
      wireEvents();
      render(state.date);
    })
    .catch(function (err) {
      showError("Sorry — the protein catalogue could not be loaded. (" + err.message + ")");
    });
})();
