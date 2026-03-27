const canvas = document.getElementById("trendChart");

if (canvas && Array.isArray(window.__TREND_POINTS__) && window.__TREND_POINTS__.length > 1) {
    const ctx = canvas.getContext("2d");
    const points = window.__TREND_POINTS__;
    const width = canvas.width = canvas.parentElement.clientWidth;
    const height = canvas.height = 250;
    const padding = 26;

    const values = points.map((point) => point.total_revenue_at_risk);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const scaleX = (index) => padding + (index * (width - padding * 2)) / (points.length - 1);
    const scaleY = (value) => {
        const range = maxValue - minValue || 1;
        return height - padding - ((value - minValue) / range) * (height - padding * 2);
    };

    ctx.clearRect(0, 0, width, height);

    ctx.strokeStyle = "rgba(31, 42, 42, 0.14)";
    ctx.lineWidth = 1;
    for (let i = 0; i < 4; i += 1) {
        const y = padding + (i * (height - padding * 2)) / 3;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }

    const gradient = ctx.createLinearGradient(0, padding, 0, height - padding);
    gradient.addColorStop(0, "rgba(13, 107, 95, 0.35)");
    gradient.addColorStop(1, "rgba(13, 107, 95, 0.02)");

    ctx.beginPath();
    ctx.moveTo(scaleX(0), height - padding);
    points.forEach((point, index) => {
        ctx.lineTo(scaleX(index), scaleY(point.total_revenue_at_risk));
    });
    ctx.lineTo(scaleX(points.length - 1), height - padding);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.beginPath();
    points.forEach((point, index) => {
        const x = scaleX(index);
        const y = scaleY(point.total_revenue_at_risk);
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.strokeStyle = "#0d6b5f";
    ctx.lineWidth = 3;
    ctx.stroke();

    points.forEach((point, index) => {
        const x = scaleX(index);
        const y = scaleY(point.total_revenue_at_risk);
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = "#0d6b5f";
        ctx.fill();
    });

    ctx.fillStyle = "#6f7468";
    ctx.font = "12px Georgia";
    points.forEach((point, index) => {
        const x = scaleX(index);
        ctx.fillText(point.snapshot_date.slice(5), x - 16, height - 8);
    });
}
