// Sale del screensaver ante cualquier input, replicando el comportamiento del
// screensaver stock de Omarchy (`read -n1` en omarchy-screensaver).
//
// Una pagina no puede matar su propio proceso, asi que avisa al servidor local
// que la sirve (bin/matrix-screensaver) y ese se encarga de bajar Chromium.
//
// Se inyecta en tiempo de ejecucion: vendor/matrix/ queda sin tocar.

(() => {
	"use strict";

	// La windowrule de Omarchy para org.omarchy.screensaver usa animation="slide"
	// (/usr/share/omarchy/default/hypr/apps/system.lua). La ventana entra
	// deslizandose por debajo de un cursor quieto, y eso emite mousemove con
	// coordenadas que cambian solas. Por eso el mouse no se arma por tiempo fijo
	// sino recien cuando la ventana se quedo quieta: cada mousemove o resize
	// reinicia el conteo, y al cesar la animacion el silencio arma el disparador.
	const SETTLE_MS = 700;
	// Piso absoluto antes de armar nada, incluso el teclado.
	const MIN_MS = 400;
	// Un mouse apoyado igual manda jitter de un pixel o dos.
	const MOVE_THRESHOLD_PX = 10;

	const startedAt = Date.now();
	let settleTimer = null;
	let mouseArmed = false;
	let anchor = null;
	let done = false;

	document.documentElement.style.cursor = "none";

	// Le confirma al servidor que la inyeccion llego a la pagina. Sin esto, un
	// fallo de inyeccion se ve igual que un screensaver que no sale nunca.
	fetch("/__ready").catch(() => {});

	const exit = (reason) => {
		if (done) return;
		done = true;
		// keepalive: la request tiene que sobrevivir a que se cierre la pagina.
		fetch("/__exit?reason=" + encodeURIComponent(reason), { keepalive: true }).catch(() => {});
		window.close();
	};

	const pastMinimum = () => Date.now() - startedAt >= MIN_MS;

	const restartSettle = () => {
		mouseArmed = false;
		anchor = null;
		clearTimeout(settleTimer);
		settleTimer = setTimeout(() => {
			mouseArmed = true;
		}, SETTLE_MS);
	};

	const onMove = (event) => {
		if (!mouseArmed || !pastMinimum()) {
			restartSettle();
			return;
		}
		if (anchor == null) {
			anchor = { x: event.screenX, y: event.screenY };
			return;
		}
		if (Math.hypot(event.screenX - anchor.x, event.screenY - anchor.y) > MOVE_THRESHOLD_PX) {
			exit("mousemove");
		}
	};

	addEventListener("mousemove", onMove, { passive: true });
	addEventListener("resize", restartSettle, { passive: true });

	// Teclado, click y rueda no tienen fuente espuria: alcanza con el piso.
	for (const type of ["keydown", "mousedown", "wheel", "touchstart"]) {
		addEventListener(type, () => pastMinimum() && exit(type), { passive: true });
	}

	// Si el screensaver perdio el foco ya no esta tapando nada.
	addEventListener("blur", () => mouseArmed && exit("blur"));

	restartSettle();
})();
