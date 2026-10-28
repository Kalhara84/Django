/* expire-form.js — Client-side logic for the expire entry add/edit form.
   Responsibilities:
     1. Dynamically add and remove detail line rows in the formset table.
     2. Keep Django's TOTAL_FORMS management input in sync with the actual
        number of visible rows so the server processes the correct count.
     3. Mark all line-form inputs as required so the browser and the custom
        submit validator catch empty fields before the form is sent.
     4. Validate all required fields on submit and highlight any that are
        empty using Bootstrap's .is-invalid red-border class.

   This file is loaded by expire/form.html via {% block scripts %} after
   Bootstrap JS has been loaded from base.html. */

/* IIFE (Immediately Invoked Function Expression) wrapper pattern.
   The entire script runs inside an anonymous function that is called
   immediately. This prevents all variables (form, body, tpl, etc.)
   from leaking into the global window scope and potentially conflicting
   with other scripts on the page. */
(function () {
  // Reference to the main form element (id="expForm" in expire/form.html)
  var form = document.getElementById('expForm');
  // Reference to the formset <tbody> (id="lineBody") where line rows live
  var body = document.getElementById('lineBody');
  // Reference to the hidden <template id="lineTemplate"> that holds the
  // blank formset row (formset.empty_form rendered by _row.html)
  var tpl = document.getElementById('lineTemplate');
  // Reference to Django's TOTAL_FORMS hidden input (name="lines-TOTAL_FORMS").
  // Django reads this on POST to know how many line forms to validate.
  var total = form.querySelector('[name="lines-TOTAL_FORMS"]');
  // Reference to the read-only "Total Lines" display input (id="totalLines")
  // shown in the totals row at the bottom of the form
  var totalBox = document.getElementById('totalLines');

  /* renumber()
     Called after every row addition or removal to keep the DOM consistent.
     Steps:
       1. Selects all <tr class="line-row"> elements in the <tbody>.
       2. Updates the .line-no cell of each row to show i+1 (1-based index).
       3. Re-writes the `name` and `id` attributes of every input/select
          inside each row, replacing the old numeric index (or __prefix__)
          with the new sequential index `i`.  This ensures Django receives
          correctly-named fields like "lines-0-exlexssno", "lines-1-exlexssno",
          etc. when the form is submitted.
       4. Updates TOTAL_FORMS to the current row count so Django processes
          exactly that many line forms.
       5. Updates the visible "Total Lines" read-only display field. */
  function renumber() {
    var rows = body.querySelectorAll('tr.line-row');
    rows.forEach(function (tr, i) {
      // Update the row number cell display
      tr.querySelector('.line-no').textContent = i + 1;
      // Re-index all name and id attributes in this row
      tr.querySelectorAll('[name],[id]').forEach(function (el) {
        ['name', 'id'].forEach(function (a) {
          var v = el.getAttribute(a);
          // Replace "lines-<digit or __prefix__>-" with "lines-<i>-"
          if (v) el.setAttribute(a, v.replace(/lines-(\d+|__prefix__)-/, 'lines-' + i + '-'));
        });
      });
    });
    // Keep Django's management form in sync
    total.value = rows.length;
    // Keep the visible Total Lines display field in sync
    totalBox.value = rows.length;
  }

  /* markRequired(scope)
     Adds the HTML `required` attribute to every <input> and <select>
     inside `scope` whose name starts with "lines-".
     This enables both native browser "please fill in this field" bubbles
     AND ensures the submit validator (below) treats them as mandatory.
     Called on the initial <tbody> contents (to mark existing rows) and
     on every newly cloned row (via addRowAfter). */
  function markRequired(scope) {
    scope.querySelectorAll('input, select').forEach(function (el) {
      if (el.name && el.name.indexOf('lines-') === 0) el.required = true;
    });
  }

  /* addRowAfter(tr)
     Clones the hidden <template id="lineTemplate"> content to create a
     new blank line row and inserts it after the given <tr> reference.
     Steps:
       1. Clone the first element child of the template (the blank <tr>).
       2. Mark all line inputs in the clone as required.
       3. Insert the clone after `tr` (or append to the end if tr is null
          or has no next sibling).
       4. Call renumber() to assign the correct index to the new row's
          fields and update TOTAL_FORMS.
       5. Focus the first input/select in the new row for convenience. */
  function addRowAfter(tr) {
    var row = tpl.content.firstElementChild.cloneNode(true);
    markRequired(row);
    if (tr && tr.nextSibling) body.insertBefore(row, tr.nextSibling); else body.appendChild(row);
    renumber();
    var first = row.querySelector('select, input');
    if (first) first.focus();
  }

  /* Click event listener on the <tbody>
     Uses event delegation (listening on the parent <tbody> rather than
     individual buttons) so that it works for both existing rows and
     dynamically cloned rows.
     .btn-add-row (+) : calls addRowAfter() to insert a new blank row
                        after the row containing the clicked button.
     .btn-del-row (-) : removes the row from the DOM if more than one
                        row exists; if it is the last remaining row, it
                        clears all inputs instead of removing the row
                        (the formset requires at least one form). */
  body.addEventListener('click', function (e) {
    var add = e.target.closest('.btn-add-row');
    var del = e.target.closest('.btn-del-row');
    if (add) { addRowAfter(add.closest('tr')); }
    if (del) {
      var tr = del.closest('tr');
      if (body.querySelectorAll('tr.line-row').length > 1) { tr.remove(); renumber(); }
      else {                                   // last row: clear only
        // Clear all field values and remove any red-border validation state
        // (.is-invalid is Bootstrap's class that shows a red border on an input)
        tr.querySelectorAll('select, input').forEach(function (el) { el.value = ''; el.classList.remove('is-invalid'); });
      }
    }
  });

  // Remove the .is-invalid red-border class as soon as the user starts
  // correcting a field (input = typing, change = selecting from dropdown)
  // .is-invalid is Bootstrap's CSS class that applies a red border to an input
  form.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });
  form.addEventListener('change', function (e) { e.target.classList.remove('is-invalid'); });

  /* Submit event listener — custom required-field validation.
     Runs before the form data is sent to the server.
     Iterates every input and select that has the `required` attribute,
     checks if its value is empty or whitespace-only, and:
       - Adds .is-invalid (Bootstrap's red-border class) to bad fields.
       - Removes .is-invalid from fields that are now valid.
       - Tracks the first invalid field found.
     If any invalid field was found, prevents form submission (e.preventDefault()),
     smoothly scrolls the first bad field into view, and focuses it so the
     user knows exactly where to fix. */
  form.addEventListener('submit', function (e) {
    var first = null;
    form.querySelectorAll('input[required], select[required]').forEach(function (el) {
      var bad = !el.value || !el.value.trim();
      // .is-invalid is Bootstrap's CSS class that draws a red border around the input
      el.classList.toggle('is-invalid', bad);
      if (bad && !first) first = el;
    });
    if (first) {
      e.preventDefault(); // stop form submission
      first.scrollIntoView({ behavior: 'smooth', block: 'center' });
      first.focus();
    }
  });

  // On page load: mark existing rows as required and renumber them
  // (ensures correct indices if the formset rendered with pre-populated data)
  markRequired(body);
  renumber();
})();
