// SVG images cannot receive clicks internally. Reload with a fresh URL so
// browsers create a new SVG animation timeline instead of reusing a cached one.
let replayCount = 0;
for (const control of document.querySelectorAll('[data-summary-replay], a[href$="/summary.html"]')) {
  const picture = control.querySelector('picture');
  if (!picture) continue;
  control.title = 'Click to replay the summary animation';
  control.addEventListener('click', event => {
    if (control.tagName === 'A' && (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey)) return;
    event.preventDefault();
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const stamp = `${Date.now()}-${++replayCount}`;
    const freshURL = path => {
      const url = new URL(path, document.baseURI);
      url.searchParams.set('replay', stamp);
      return url.href;
    };
    for (const source of picture.querySelectorAll('source')) {
      source.srcset = freshURL(source.getAttribute('srcset'));
    }
    const image = picture.querySelector('img');
    image.src = freshURL(image.getAttribute('src'));
  });
}
