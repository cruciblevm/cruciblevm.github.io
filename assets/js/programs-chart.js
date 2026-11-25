// Grows the real-programs chart's bars once it scrolls into view; without this script, or with reduced motion, they simply show.
(function () {
  var chart = document.querySelector(".programs-chart");
  if (!chart || !("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }
  chart.classList.add("will-animate");
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        // A frame after the start state is painted, so the transition runs.
        requestAnimationFrame(function () { chart.classList.add("in-view"); });
        observer.disconnect();
      }
    });
  }, { threshold: 0.25 });
  observer.observe(chart);
})();
