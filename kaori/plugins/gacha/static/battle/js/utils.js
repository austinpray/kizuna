export async function sleep(msec) {
  return new Promise(function (resolve) {
    window.setTimeout(function () {
      resolve();
    }, msec);
  })
}

export async function animate(el, className, durationMs = 1000) {
  return new Promise(resolve => {
    let tokens = ['animate__animated', ...[className].flat(Infinity)];
    el.classList.add(...tokens);
    el.style.setProperty('--animate-duration', `${durationMs}ms`)

    const finish = () => {
      el.classList.remove(...tokens)
      resolve(el)
    };

    // fallthrough if animation never starts
    const timeout = window.setTimeout(finish, durationMs)
    el.addEventListener('animationstart', _ => window.clearTimeout(timeout));

    el.addEventListener('animationend', finish);
  });
}

function linearScale({x, xMin, xMax, a, b}) {
  return a + (x - xMin) * (b - a) / (xMax - xMin)
}

export function relativeColor(value, {min = 1, max = 100, linear = false}) {

  const ranges = {
    xMin: min,
    xMax: max,
    a: 0,
    b: 255,
  }

  let R = 0
  if (linear) {
    R = linearScale({x: max - value, ...ranges});
  }
  let G = linearScale({x: value, ...ranges});

  return `rgb(${R},${G},0)`;


}

export function sanitizeHtml(str) {
  const decoder = document.createElement('div')
  decoder.innerHTML = str
  return decoder.textContent
}