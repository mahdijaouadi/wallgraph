const canvas = document.getElementById("backgroundCanvas");
const ctx = canvas.getContext("2d");

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener("resize", resizeCanvas);

const NUM_STARS = 100;               // Total particles
const SPECIAL_STAR_CHANCE = 0.1;    // Chance for bullish/bearish arrow

// Initialize particles
const stars = Array.from({ length: NUM_STARS }, () => createStar());

function createStar() {
  return {
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    radius: Math.random() * 2 + 1,    // Normal star size
    speed: Math.random() * 1 + 0.02,   // Falling speed
    special: Math.random() < SPECIAL_STAR_CHANCE,
    type: Math.random() < 0.5 ? "bull" : "bear" // For special arrows
  };
}

// Animate loop
export async function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  stars.forEach(star => {
    drawStar(star);
    updateStarPosition(star);
  });

  requestAnimationFrame(animate);
}

// Draw each particle
function drawStar(star) {
  ctx.save();
  ctx.translate(star.x, star.y);

  if (star.special) {
    ctx.fillStyle = star.type === "bull" ? "green" : "red";
    ctx.shadowBlur = 10;
    ctx.shadowColor = ctx.fillStyle;
    drawArrow(ctx, star.radius + 2, star.type); // Pass type to arrow
  } else {
    ctx.beginPath();
    ctx.fillStyle = "white";
    ctx.arc(0, 0, star.radius, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.restore();
}

// Arrow shape (up for bull, down for bear)
function drawArrow(ctx, size, type) {
  ctx.beginPath();
  if (type === "bull") {
    ctx.moveTo(0, -size);        // Tip up
    ctx.lineTo(size / 2, size);  // Bottom right
    ctx.lineTo(-size / 2, size); // Bottom left
  } else {
    ctx.moveTo(0, size);         // Tip down
    ctx.lineTo(size / 2, -size); // Top right
    ctx.lineTo(-size / 2, -size);// Top left
  }
  ctx.closePath();
  ctx.fill();
}


// Update position for falling effect
function updateStarPosition(star) {
  star.y += star.speed;

  if (star.y > canvas.height) {
    star.y = 0;
    star.x = Math.random() * canvas.width;
    star.special = Math.random() < SPECIAL_STAR_CHANCE;
    star.type = Math.random() < 0.5 ? "bull" : "bear";
  }
}