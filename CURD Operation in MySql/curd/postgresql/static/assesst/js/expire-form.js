/* =============================================================================
   expire-form.js - JavaScript of the Expire entry form
   =============================================================================
   Loaded by templates/postgresql/expire/form.html ({% block scripts %}).
   Part 1: + / - buttons that add and remove table rows (lines = exlmast)
   Part 2: check empty fields before Save (the server checks again: expire_forms.py)
   Part 3: "Add Location" pop-up (saves to exlocmast via expire_views.location_add)
   ============================================================================= */

/* ---------- Parts 1 and 2: rows and validation ---------- */
(function () {
  // Elements of form.html
  var form = document.getElementById('expForm');
  var body = document.getElementById('lineBody');            // <tbody> of the lines table
  var tpl = document.getElementById('lineTemplate');         // blank row to copy
  var total = form.querySelector('[name="lines-TOTAL_FORMS"]'); // Django needs the number of rows
  var totalBox = document.getElementById('totalLines');      // "Total Lines" box

  // Give every row its number (1, 2, 3 ...) and the field names Django expects
  // (lines-0-..., lines-1-...). Runs after a row is added or removed.
  function renumber() {
    var rows = body.querySelectorAll('tr.line-row');
    rows.forEach(function (tr, i) {
      tr.querySelector('.line-no').textContent = i + 1;
      tr.querySelectorAll('[name],[id]').forEach(function (el) {
        ['name', 'id'].forEach(function (a) {
          var v = el.getAttribute(a);
          if (v) el.setAttribute(a, v.replace(/lines-(\d+|__prefix__)-/, 'lines-' + i + '-'));
        });
      });
    });
    total.value = rows.length;
    totalBox.value = rows.length;
  }

  // Row fields are required (the copied blank row does not have the attribute)
  function markRequired(scope) {
    scope.querySelectorAll('input, select').forEach(function (el) {
      if (el.name && el.name.indexOf('lines-') === 0) el.required = true;
    });
  }

  // + button: copy the blank row and put it under the clicked row
  function addRowAfter(tr) {
    var row = tpl.content.firstElementChild.cloneNode(true);
    markRequired(row);
    if (tr && tr.nextSibling) body.insertBefore(row, tr.nextSibling); else body.appendChild(row);
    renumber();
    var first = row.querySelector('select, input');
    if (first) first.focus();
  }

  // + and - button clicks (one listener for the whole table)
  body.addEventListener('click', function (e) {
    var add = e.target.closest('.btn-add-row');
    var del = e.target.closest('.btn-del-row');
    if (add) { addRowAfter(add.closest('tr')); }
    if (del) {
      var tr = del.closest('tr');
      if (body.querySelectorAll('tr.line-row').length > 1) { tr.remove(); renumber(); }
      else {
        // Last row cannot be removed, so just clear it
        tr.querySelectorAll('select, input').forEach(function (el) { el.value = ''; el.classList.remove('is-invalid'); });
      }
    }
  });

  // Remove the red border as soon as the user changes the field
  form.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });
  form.addEventListener('change', function (e) { e.target.classList.remove('is-invalid'); });

  // Save button: stop the submit if a required field is empty and show it in red
  form.addEventListener('submit', function (e) {
    var first = null;
    form.querySelectorAll('input[required], select[required]').forEach(function (el) {
      var bad = !el.value || !el.value.trim();
      el.classList.toggle('is-invalid', bad);
      if (bad && !first) first = el;
    });
    if (first) {
      e.preventDefault();
      first.scrollIntoView({ behavior: 'smooth', block: 'center' });
      first.focus();
    }
  });

  // On page load
  markRequired(body);
  renumber();
})();


/* ---------- Part 3: "Add Location" pop-up ---------- */
(function () {
  // Elements of the pop-up (form.html, #locModal)
  var modalEl = document.getElementById('locModal');
  var locForm = document.getElementById('locForm');
  var codeBox = document.getElementById('locCode');
  var nameBox = document.getElementById('locName');
  var saveBtn = document.getElementById('locSave');
  var generalErr = document.getElementById('locError');      // error that is not about one field

  // The Location combo box of the main form (HeaderForm.exhexlocsno)
  var select = document.getElementById('id_exhexlocsno');

  // Django's security token, read from the main form
  var csrf = document.querySelector('#expForm [name="csrfmiddlewaretoken"]').value;

  // Show an error under one input (the red text is the next element)
  function showError(box, msg) {
    box.classList.add('is-invalid');
    box.nextElementSibling.textContent = msg;
  }

  // Clear all errors in the pop-up
  function clearErrors() {
    [codeBox, nameBox].forEach(function (b) { b.classList.remove('is-invalid'); });
    generalErr.classList.add('d-none');
    generalErr.textContent = '';
  }

  // Add the new <option> in alphabetical order (the list is sorted by location code)
  function addOption(id, label) {
    var opt = new Option(label, id, true, true);
    var before = null;
    for (var i = 1; i < select.options.length; i++) {          // 0 = "-- Select --"
      if (select.options[i].text.toLowerCase() > label.toLowerCase()) { before = select.options[i]; break; }
    }
    select.add(opt, before);
    select.value = id;                                          // select the new location
    select.classList.remove('is-invalid');
  }

  // Every time the pop-up opens: start with empty boxes
  modalEl.addEventListener('show.bs.modal', function () {
    codeBox.value = '';
    nameBox.value = '';
    clearErrors();
  });

  // After it is open: put the cursor in the code box
  modalEl.addEventListener('shown.bs.modal', function () { codeBox.focus(); });

  // Remove the red border when the user types
  locForm.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });

  // Save button of the pop-up
  locForm.addEventListener('submit', function (e) {
    e.preventDefault();                                         // do not reload the page
    clearErrors();

    // 1) check on the browser
    var code = codeBox.value.trim(), name = nameBox.value.trim(), bad = false;
    if (!code) { showError(codeBox, 'Location Code is required'); bad = true; }
    if (!name) { showError(nameBox, 'Location Name is required'); bad = true; }
    if (bad) return;

    // 2) send to the server (views.location_add). It checks again and saves to exlocmast.
    saveBtn.disabled = true;                                    // stop double clicks
    fetch(modalEl.dataset.url, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ exlocloc: code, exlocnam: name })
    })
      .then(function (r) { return r.json().then(function (data) { return { ok: r.ok, data: data }; }); })
      .then(function (res) {
        if (res.ok && res.data.ok) {
          // Saved: add it to the combo box, select it and close the pop-up
          addOption(res.data.id, res.data.label);
          bootstrap.Modal.getOrCreateInstance(modalEl).hide();
        } else {
          // Not saved: show the server messages (e.g. "This Location Code already exists")
          var errs = (res.data && res.data.errors) || {};
          if (errs.exlocloc) showError(codeBox, errs.exlocloc);
          if (errs.exlocnam) showError(nameBox, errs.exlocnam);
          if (errs.__all__) { generalErr.textContent = errs.__all__; generalErr.classList.remove('d-none'); }
        }
      })
      .catch(function () {
        // Network error, or the login ended
        generalErr.textContent = 'Could not save. Please try again.';
        generalErr.classList.remove('d-none');
      })
      .then(function () { saveBtn.disabled = false; });
  });
})();
