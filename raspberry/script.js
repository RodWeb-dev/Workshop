async function fetchData() {
    const res = await fetch('data.php');
    return res.json();
}

function updateCurrentValues(data) {
    document.querySelector('[data-temp-value]').textContent = `${data.temp} °C`;
    document.querySelector('[data-hygro-value]').textContent = `${data.hygro} %`;
    document.querySelector('[data-lux-value]').textContent = `${data.lux} lx`;
}

function updateEquipements(events) {
    const actifs = new Set(events.map(event => `data-${event.id}`));
    document.querySelectorAll('.voyant').forEach(voyant => {
        const attr = voyant.getAttributeNames().find(name => /^data-\d+$/.test(name));
        voyant.classList.toggle('on', actifs.has(attr));
    });
}

function formatDuration(totalSeconds) {
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = Math.floor(totalSeconds % 60);
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
}

function updateEquipementsStats(stats) {
    Object.entries(stats).forEach(([id, stat]) => {
        const cyclesEl = document.querySelector(`[data-cycles-${id}]`);
        const durationEl = document.querySelector(`[data-duration-${id}]`);
        if (cyclesEl) cyclesEl.textContent = `${stat.cycles} cycle${stat.cycles > 1 ? 's' : ''}`;
        if (durationEl) durationEl.textContent = formatDuration(stat.duration);
    });
}

const tabConfig = {
    temp: { label: 'Température (°C)', color: '#e63946', field: 'temp', min:10, max: 30 },
    hygro: { label: 'Humidité (%)', color: '#457b9d', field: 'hygro', min: 20, max: 60 },
    lux: { label: 'Luminosité (lx)', color: '#f4a261', field: 'lux', min: 0, max: 100 },
};

let chart;
let latestReadings = [];
let currentTab = 'temp';

function initChart() {
    const ctx = document.getElementById('readingChart');
    const cfg = tabConfig[currentTab];
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{ label: cfg.label, data: [], borderColor: cfg.color, tension: 0.3, pointRadius: 0 }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: { x: { display: false }, y: { beginAtZero: false } }
        }
    });
}

function renderChart() {
    const cfg = tabConfig[currentTab];
    chart.data.labels = latestReadings.map(r => new Date(r.recorded_at).toLocaleTimeString());
    chart.data.datasets[0].label = cfg.label;
    chart.data.datasets[0].borderColor = cfg.color;
    chart.data.datasets[0].data = latestReadings.map(r => r[cfg.field]);
    chart.options.scales.y.min = cfg.min;
    chart.options.scales.y.max = cfg.max;
    chart.update();
}

function setupTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentTab = tab.dataset.tab;
            renderChart();
        });
    });
}

async function refresh() {
    try {
        const { actualRealData, actualEvent, readings, equipementsStats } = await fetchData();
        if (actualRealData) updateCurrentValues(actualRealData);
        if (actualEvent) updateEquipements(actualEvent);
        if (equipementsStats) updateEquipementsStats(equipementsStats);
        if (readings) {
            latestReadings = readings;
            renderChart();
        }
    } catch (err) {
        console.error('Erreur lors de la récupération des données', err);
    }
}

initChart();
setupTabs();
refresh();
setInterval(refresh, 1000);
