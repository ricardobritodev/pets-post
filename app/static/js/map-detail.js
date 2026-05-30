(function () {
  var el = document.getElementById('detail-map');
  if (!el) return;

  var lat   = parseFloat(el.dataset.lat);
  var lng   = parseFloat(el.dataset.lng);
  var label = el.dataset.label || '';
  var zoom  = parseInt(el.dataset.zoom, 10) || 15;

  var map = L.map('detail-map').setView([lat, lng], zoom);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19
  }).addTo(map);
  L.marker([lat, lng]).addTo(map).bindPopup(label).openPopup();
}());
