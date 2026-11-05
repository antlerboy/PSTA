/* Prepare an enquiry on the visitor's device. Sending remains their action. */
(function () {
  'use strict';
  const form = document.querySelector('[data-practice-intake]');
  if (!form) return;
  const output = document.getElementById('intake-preview');
  const status = document.getElementById('intake-status');
  function draft() {
    const lines = [form.dataset.heading, ''];
    for (const control of form.querySelectorAll('[data-prompt]')) {
      lines.push(control.dataset.prompt + ':', control.value.trim() || '(To discuss)', '');
    }
    return lines.join('\n');
  }
  function refresh() { output.textContent = draft(); }
  form.addEventListener('input', refresh);
  form.addEventListener('submit', event => {
    event.preventDefault();
    const text = draft();
    if (text.length > 5000) { status.textContent = 'This is a long enquiry. Download the text and paste it into an email to ' + form.dataset.recipient + '.'; return; }
    window.location.href = 'mailto:' + form.dataset.recipient + '?subject=' + encodeURIComponent(form.dataset.heading) + '&body=' + encodeURIComponent(text);
    status.textContent = 'Check for a draft in your email app, and send it when you’re ready. If no draft opens, download the text below.';
  });
  document.getElementById('intake-download').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([draft()], { type: 'text/plain;charset=utf-8' }));
    const a = document.createElement('a'); a.href = url; a.download = 'psta-enquiry.txt'; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
    status.textContent = 'The enquiry text has been downloaded. It has not been sent.';
  });
  refresh();
})();
