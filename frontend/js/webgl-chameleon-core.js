/**
 * ChameleonShell: Interactive 3D Deception Core (WebGL / Three.js)
 * Clean, sculptural geodesic icosahedron with subtle crystalline core,
 * single tactical orbit ring, continuous auto-rotation, dynamic cursor-velocity
 * acceleration surge, and active threat pulse mechanics.
 */

let coreState = {
  mode: 'shield', // 'shield' | 'radar' | 'canary'
  isThreatPulsing: false,
  threatDecay: 0,
};

function initHeroWebGLCore() {
  const container = document.getElementById('hero-canvas-container');
  if (!container || !window.THREE) {
    if (!window.THREE) {
      console.warn('[WebGL Core] THREE is not loaded on window.');
    }
    return;
  }

  // Prevent duplicate canvas instantiation
  if (container.querySelector('canvas')) {
    return;
  }

  const w = container.clientWidth || 480;
  const h = container.clientHeight || 420;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(56, w / h, 0.1, 1000);
  camera.position.z = 4.85;

  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' });
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // Mount canvas before HUD overlay to keep HUD visible on top
  const hud = container.querySelector('.canvas-overlay-hud');
  if (hud) {
    container.insertBefore(renderer.domElement, hud);
  } else {
    container.appendChild(renderer.domElement);
  }

  // 1. Group for all rotating elements
  const coreGroup = new THREE.Group();
  scene.add(coreGroup);

  // 2. Clean, Sculptural Outer Icosahedron Wireframe in #D4FF00
  // Detail 1 gives an elegant, balanced geodesic structure (80 triangles)
  const outerGeo = new THREE.IcosahedronGeometry(2.08, 1);
  const outerMat = new THREE.MeshBasicMaterial({
    color: 0xD4FF00,
    wireframe: true,
    transparent: true,
    opacity: 0.28,
  });
  const outerMesh = new THREE.Mesh(outerGeo, outerMat);
  coreGroup.add(outerMesh);

  // 3. Delicate Micro-Vertex Points (Tiny, unobtrusive node accents)
  const vertexPositions = outerGeo.attributes.position.array;
  const vertexPointsGeo = new THREE.BufferGeometry();
  vertexPointsGeo.setAttribute('position', new THREE.BufferAttribute(vertexPositions, 3));
  const vertexMat = new THREE.PointsMaterial({
    color: 0xD4FF00,
    size: 0.024,
    transparent: true,
    opacity: 0.6,
  });
  const vertexPoints = new THREE.Points(vertexPointsGeo, vertexMat);
  coreGroup.add(vertexPoints);

  // 4. Single Ultra-Sleek Tactical Orbit Ring (Equatorial plane)
  const ringGeo = new THREE.RingGeometry(2.44, 2.455, 64);
  const ringMat = new THREE.MeshBasicMaterial({
    color: 0x00FF9D,
    wireframe: true,
    transparent: true,
    opacity: 0.18,
    side: THREE.DoubleSide,
  });
  const orbitRing = new THREE.Mesh(ringGeo, ringMat);
  orbitRing.rotation.x = Math.PI / 3.2;
  coreGroup.add(orbitRing);

  // 5. Crystalline Inner Core (Emerald Diamond Lattice + Glowing Energy Node)
  const innerLatticeGeo = new THREE.OctahedronGeometry(0.72, 0);
  const innerLatticeMat = new THREE.MeshBasicMaterial({
    color: 0x00FF9D,
    wireframe: true,
    transparent: true,
    opacity: 0.45,
  });
  const innerLattice = new THREE.Mesh(innerLatticeGeo, innerLatticeMat);
  coreGroup.add(innerLattice);

  const innerGeo = new THREE.SphereGeometry(0.32, 24, 24);
  const innerMat = new THREE.MeshBasicMaterial({
    color: 0x00FF9D,
    transparent: true,
    opacity: 0.85,
  });
  const innerMesh = new THREE.Mesh(innerGeo, innerMat);
  coreGroup.add(innerMesh);

  // 6. Interaction State & Continuous Rotation Mechanics
  const baseRotationY = 0.0032; // Always rotating continuously
  const baseRotationX = 0.0012;
  let cursorSpinBoost = 0;
  let spinDirection = 1;
  let lastMouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
  let targetTiltX = 0;
  let targetTiltY = 0;
  let currentTiltX = 0;
  let currentTiltY = 0;

  // Track cursor movement across window to accelerate spin
  window.addEventListener('pointermove', (e) => {
    const dx = e.clientX - lastMouse.x;
    const dy = e.clientY - lastMouse.y;
    const dist = Math.hypot(dx, dy);
    lastMouse = { x: e.clientX, y: e.clientY };

    if (dist > 1.2) {
      // Dynamic acceleration burst proportional to cursor velocity
      const impulse = Math.min(dist * 0.00075, 0.045);
      cursorSpinBoost += impulse;
      cursorSpinBoost = Math.min(cursorSpinBoost, 0.075); // Velocity cap for stability

      // Cursor movement direction influences spin
      if (Math.abs(dx) > 3) {
        spinDirection = dx > 0 ? 1 : -1;
      }
    }

    // Subtle 3D perspective parallax tilt
    targetTiltX = (e.clientY / window.innerHeight - 0.5) * 0.35;
    targetTiltY = (e.clientX / window.innerWidth - 0.5) * 0.35;
  }, { passive: true });

  // Direct Drag-to-Rotate on Canvas
  let isDragging = false;
  let previousDragPos = { x: 0, y: 0 };
  let dragDelta = { x: 0, y: 0 };

  renderer.domElement.addEventListener('pointerdown', (e) => {
    isDragging = true;
    previousDragPos = { x: e.clientX, y: e.clientY };
  });

  window.addEventListener('pointermove', (e) => {
    if (isDragging) {
      const dx = e.clientX - previousDragPos.x;
      const dy = e.clientY - previousDragPos.y;
      dragDelta = { x: dx * 0.005, y: dy * 0.005 };
      coreGroup.rotation.y += dragDelta.x;
      coreGroup.rotation.x += dragDelta.y;
      previousDragPos = { x: e.clientX, y: e.clientY };
    }
  }, { passive: true });

  window.addEventListener('pointerup', () => {
    isDragging = false;
  });

  // Zoom control on canvas
  renderer.domElement.addEventListener('wheel', (e) => {
    e.preventDefault();
    camera.position.z += e.deltaY * 0.002;
    camera.position.z = Math.min(Math.max(camera.position.z, 3.8), 6.2);
  }, { passive: false });

  // Global Threat Shockwave Trigger
  window.triggerCoreThreatPulse = function (threatType = 'probe', customText = null) {
    coreState.isThreatPulsing = true;
    coreState.threatDecay = 1.0;
    cursorSpinBoost += 0.05; // Spin burst on threat inject

    if (threatType === 'crimson') {
      outerMat.color.setHex(0xFF2A54);
      vertexMat.color.setHex(0xFF2A54);
      innerMat.color.setHex(0xFF2A54);
      innerLatticeMat.color.setHex(0xFF2A54);
    } else if (threatType === 'canary') {
      outerMat.color.setHex(0xFFAA00);
      vertexMat.color.setHex(0xFFAA00);
      innerMat.color.setHex(0xFFAA00);
      innerLatticeMat.color.setHex(0xFFAA00);
    } else {
      outerMat.color.setHex(0xD4FF00);
      vertexMat.color.setHex(0xD4FF00);
      innerMat.color.setHex(0x00FF9D);
      innerLatticeMat.color.setHex(0x00FF9D);
    }

    coreGroup.rotation.y += 0.35 * spinDirection;
    coreGroup.rotation.x += 0.15;

    const statusText = document.getElementById('core-status-text');
    if (statusText) {
      statusText.innerHTML = customText
        ? `<span style="color:#FF2A54">[PROBE] ${customText}</span>`
        : `<span style="color:#D4FF00">[PROBE TRAPPED] 3.2ms FAST-PATH</span>`;
    }
  };

  // Global Mode Setter
  window.setCoreMode = function (modeName) {
    coreState.mode = modeName;
    if (modeName === 'canary') {
      outerMat.color.setHex(0xFFAA00);
      outerMat.opacity = 0.42;
      innerMat.color.setHex(0xFF2A54);
      innerLatticeMat.color.setHex(0xFFAA00);
      ringMat.color.setHex(0xFFAA00);
    } else if (modeName === 'radar') {
      outerMat.color.setHex(0x00FF9D);
      outerMat.opacity = 0.38;
      innerMat.color.setHex(0x00FF9D);
      innerLatticeMat.color.setHex(0x00FF9D);
      ringMat.color.setHex(0x00FF9D);
    } else {
      outerMat.color.setHex(0xD4FF00);
      outerMat.opacity = 0.28;
      innerMat.color.setHex(0x00FF9D);
      innerLatticeMat.color.setHex(0x00FF9D);
      ringMat.color.setHex(0x00FF9D);
    }
  };

  // Animation Loop (Always Rotating + Cursor Acceleration)
  let clock = 0;
  function animate() {
    requestAnimationFrame(animate);
    clock += 0.02;

    if (!isDragging) {
      // Exponential inertia decay for cursor velocity surge
      cursorSpinBoost *= 0.938;
      if (cursorSpinBoost < 0.0001) cursorSpinBoost = 0;

      // Always rotate continuously at baseline + dynamic cursor acceleration
      const activeSpeedY = (baseRotationY + cursorSpinBoost * 1.8) * spinDirection;
      const activeSpeedX = baseRotationX + cursorSpinBoost * 0.6;

      coreGroup.rotation.y += activeSpeedY;
      coreGroup.rotation.x += activeSpeedX;

      // Parallax damping
      currentTiltX += (targetTiltX - currentTiltX) * 0.035;
      currentTiltY += (targetTiltY - currentTiltY) * 0.035;
      coreGroup.position.x = currentTiltY * 0.22;
      coreGroup.position.y = -currentTiltX * 0.22;
    }

    // Secondary orbits
    orbitRing.rotation.z += 0.004;
    innerLattice.rotation.x -= 0.004;
    innerLattice.rotation.y += 0.005;

    // Organic core luminescence breathing
    const pulseScale = 1.0 + Math.sin(clock * 2.2) * 0.06;
    innerMesh.scale.set(pulseScale, pulseScale, pulseScale);

    // Threat Decay recovery
    if (coreState.isThreatPulsing) {
      coreState.threatDecay -= 0.015;
      if (coreState.threatDecay <= 0) {
        coreState.isThreatPulsing = false;
        outerMat.color.setHex(coreState.mode === 'canary' ? 0xFFAA00 : 0xD4FF00);
        vertexMat.color.setHex(0xD4FF00);
        innerMat.color.setHex(0x00FF9D);
        innerLatticeMat.color.setHex(0x00FF9D);
        const statusText = document.getElementById('core-status-text');
        if (statusText) statusText.textContent = 'CORE: HYBRID VST [ONLINE]';
      }
    }

    renderer.render(scene, camera);
  }
  animate();

  // Responsive resize
  window.addEventListener('resize', () => {
    if (!container) return;
    const curW = container.clientWidth || 480;
    const curH = container.clientHeight || 420;
    camera.aspect = curW / curH;
    camera.updateProjectionMatrix();
    renderer.setSize(curW, curH);
  }, { passive: true });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initHeroWebGLCore);
} else {
  initHeroWebGLCore();
}
