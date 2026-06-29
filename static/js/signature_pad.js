/*
 * Lightweight canvas-based signature pad.
 * Draws on the #signaturePad canvas and serializes the result as a
 * base64 PNG data URL into the hidden `signature_data` form field so
 * it can be stored with the statement and reprinted later.
 */
(function () {
    const canvas = document.getElementById("signaturePad");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.strokeStyle = "#1a3c6e";
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    let drawing = false;
    let lastX = 0;
    let lastY = 0;

    function getPos(evt) {
        const rect = canvas.getBoundingClientRect();
        const clientX = evt.touches ? evt.touches[0].clientX : evt.clientX;
        const clientY = evt.touches ? evt.touches[0].clientY : evt.clientY;
        return {
            x: ((clientX - rect.left) / rect.width) * canvas.width,
            y: ((clientY - rect.top) / rect.height) * canvas.height,
        };
    }

    function start(evt) {
        drawing = true;
        const pos = getPos(evt);
        lastX = pos.x;
        lastY = pos.y;
        evt.preventDefault();
    }

    function move(evt) {
        if (!drawing) return;
        const pos = getPos(evt);
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();
        lastX = pos.x;
        lastY = pos.y;
        evt.preventDefault();
    }

    function end() {
        if (!drawing) return;
        drawing = false;
        saveSignature();
    }

    function saveSignature() {
        const hiddenField = document.querySelector('input[name="signature_data"]');
        if (hiddenField) {
            hiddenField.value = canvas.toDataURL("image/png");
        }
    }

    canvas.addEventListener("mousedown", start);
    canvas.addEventListener("mousemove", move);
    canvas.addEventListener("mouseup", end);
    canvas.addEventListener("mouseleave", end);
    canvas.addEventListener("touchstart", start);
    canvas.addEventListener("touchmove", move);
    canvas.addEventListener("touchend", end);

    const clearBtn = document.getElementById("clearSignature");
    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            const hiddenField = document.querySelector('input[name="signature_data"]');
            if (hiddenField) hiddenField.value = "";
        });
    }
})();
