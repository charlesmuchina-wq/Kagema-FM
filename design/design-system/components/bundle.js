/* @ds-bundle: {"format":4,"namespace":"KagemaFM","components":[{"name":"PlayButton"},{"name":"NowPlayingCard"},{"name":"StationRow"},{"name":"MoreRow"},{"name":"MessageBanner"}]} */
(function () {
  'use strict';
  var SVG = 'http://www.w3.org/2000/svg';
  var PATHS = {
    play: 'M8 5v14l11-7z',
    stop: 'M6 6h12v12H6z',
    chevron: 'M9 4l8 8-8 8-2-2 6-6-6-6z',
    check: 'M9 16.2l-3.5-3.5L4 14.2l5 5 11-11-1.5-1.5z',
    wait: 'M6 2h12v5l-4 5 4 5v5H6v-5l4-5-4-5V2zm2 2v2.3l4 5 4-5V4H8z',
    warn: 'M12 2L1 21h22L12 2zm-1 7h2v6h-2V9zm0 8h2v2h-2v-2z',
    info: 'M12 2a10 10 0 100 20 10 10 0 000-20zm-1 5h2v2h-2V7zm0 4h2v6h-2v-6z',
    more: 'M4 6h16v2.5H4zm0 5h16v2.5H4zm0 5h16v2.5H4z'
  };
  function icon(name) {
    var s = document.createElementNS(SVG, 'svg');
    s.setAttribute('viewBox', '0 0 24 24');
    s.setAttribute('class', 'kfm-icon');
    s.setAttribute('aria-hidden', 'true');
    var p = document.createElementNS(SVG, 'path');
    p.setAttribute('d', PATHS[name] || PATHS.info);
    s.appendChild(p);
    return s;
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function labels(l, d) { var o = {}, k; for (k in d) o[k] = (l && l[k]) || d[k]; return o; }

  /* PlayButton({playing, onToggle, labels:{play, stop}}) */
  function PlayButton(p) {
    p = p || {};
    var L = labels(p.labels, { play: 'Play', stop: 'Stop' });
    var b = el('button', 'kfm kfm-play');
    b.type = 'button';
    var disc = el('span', 'kfm-play__disc');
    var word = el('span', 'kfm-play__word');
    b.appendChild(disc); b.appendChild(word);
    var playing = !!p.playing;
    function draw() {
      disc.textContent = '';
      disc.appendChild(icon(playing ? 'stop' : 'play'));
      word.textContent = playing ? L.stop : L.play;
      b.setAttribute('aria-label', playing ? L.stop : L.play);
      b.setAttribute('aria-pressed', String(playing));
    }
    b.addEventListener('click', function () {
      playing = !playing; draw();
      if (p.onToggle) p.onToggle(playing);
    });
    b.setPlaying = function (v) { playing = !!v; draw(); };
    draw();
    return b;
  }

  /* NowPlayingCard({name, state:'playing'|'buffering'|'error'|'stopped', labels}) */
  function NowPlayingCard(p) {
    p = p || {};
    var L = labels(p.labels, { heading: 'Now playing', headingStopped: 'Radio is off', playing: 'Playing', buffering: 'Connecting. Please wait.', error: 'No internet. Trying again.', stopped: 'Stopped' });
    var state = p.state || 'stopped';
    var ICON = { playing: 'check', buffering: 'wait', error: 'warn', stopped: 'stop' };
    var c = el('section', 'kfm kfm-now');
    c.setAttribute('aria-live', 'polite');
    c.appendChild(el('div', 'kfm-now__label', state === 'stopped' ? L.headingStopped : L.heading));
    c.appendChild(el('div', 'kfm-now__name', p.name || ''));
    var s = el('div', 'kfm-now__state kfm-now__state--' + state);
    s.appendChild(icon(ICON[state] || 'info'));
    s.appendChild(el('span', '', L[state] || state));
    c.appendChild(s);
    return c;
  }

  /* StationRow({name, meta, number, playing, onSelect, labels:{playing}}) */
  function StationRow(p) {
    p = p || {};
    var L = labels(p.labels, { playing: 'Playing' });
    var b = el('button', 'kfm kfm-row' + (p.playing ? ' kfm-row--playing' : ''));
    b.type = 'button';
    if (p.number != null) b.appendChild(el('span', 'kfm-row__num', String(p.number)));
    var t = el('span', 'kfm-row__text');
    t.appendChild(el('span', 'kfm-row__name', p.name || ''));
    var meta = p.playing ? L.playing : p.meta;
    if (meta) t.appendChild(el('span', 'kfm-row__meta', meta));
    b.appendChild(t);
    b.appendChild(icon(p.playing ? 'check' : 'play'));
    if (p.playing) b.setAttribute('aria-current', 'true');
    b.addEventListener('click', function () { if (p.onSelect) p.onSelect(p); });
    return b;
  }

  /* MoreRow({label, hint, onOpen}) */
  function MoreRow(p) {
    p = p || {};
    var b = el('button', 'kfm kfm-row');
    b.type = 'button';
    b.appendChild(icon('more'));
    var t = el('span', 'kfm-row__text');
    t.appendChild(el('span', 'kfm-row__name', p.label || 'More'));
    if (p.hint) t.appendChild(el('span', 'kfm-row__meta', p.hint));
    b.appendChild(t);
    b.appendChild(icon('chevron'));
    b.addEventListener('click', function () { if (p.onOpen) p.onOpen(); });
    return b;
  }

  /* MessageBanner({kind:'error'|'info', title, body, okLabel, onDismiss}) — stays until dismissed */
  function MessageBanner(p) {
    p = p || {};
    var kind = p.kind === 'info' ? 'info' : 'error';
    var m = el('div', 'kfm kfm-msg kfm-msg--' + kind);
    m.setAttribute('role', kind === 'error' ? 'alert' : 'status');
    var h = el('div', 'kfm-msg__head');
    h.appendChild(icon(kind === 'error' ? 'warn' : 'info'));
    h.appendChild(el('span', '', p.title || ''));
    m.appendChild(h);
    if (p.body) m.appendChild(el('div', 'kfm-msg__body', p.body));
    var ok = el('button', 'kfm-msg__ok', p.okLabel || 'OK');
    ok.type = 'button';
    ok.addEventListener('click', function () { m.remove(); if (p.onDismiss) p.onDismiss(); });
    m.appendChild(ok);
    return m;
  }

  window.KagemaFM = { PlayButton: PlayButton, NowPlayingCard: NowPlayingCard, StationRow: StationRow, MoreRow: MoreRow, MessageBanner: MessageBanner };
})();
