/* Expire entry form - detail rows (+ / -) saha client side validation */
(function () {
  var form = document.getElementById('expForm');
  var body = document.getElementById('lineBody');
  var tpl = document.getElementById('lineTemplate');
  var total = form.querySelector('[name="lines-TOTAL_FORMS"]');
  var totalBox = document.getElementById('totalLines');

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

  function markRequired(scope) {
    scope.querySelectorAll('input, select').forEach(function (el) {
      if (el.name && el.name.indexOf('lines-') === 0) el.required = true;
    });
  }

  function addRowAfter(tr) {
    var row = tpl.content.firstElementChild.cloneNode(true);
    markRequired(row);
    if (tr && tr.nextSibling) body.insertBefore(row, tr.nextSibling); else body.appendChild(row);
    renumber();
    var first = row.querySelector('select, input');
    if (first) first.focus();
  }

  body.addEventListener('click', function (e) {
    var add = e.target.closest('.btn-add-row');
    var del = e.target.closest('.btn-del-row');
    if (add) { addRowAfter(add.closest('tr')); }
    if (del) {
      var tr = del.closest('tr');
      if (body.querySelectorAll('tr.line-row').length > 1) { tr.remove(); renumber(); }
      else {                                   // last row: clear only
        tr.querySelectorAll('select, input').forEach(function (el) { el.value = ''; el.classList.remove('is-invalid'); });
      }
    }
  });

  // red border remove when user fixes the field
  form.addEventListener('input', function (e) { e.target.classList.remove('is-invalid'); });
  form.addEventListener('change', function (e) { e.target.classList.remove('is-invalid'); });

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

  markRequired(body);
  renumber();
})();
