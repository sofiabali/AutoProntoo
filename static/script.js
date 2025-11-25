// fade-in sessoes

const fadeElements = document.querySelectorAll(".fade-in");

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
      }
    });
  },
  { threshold: 0.1 }
);

fadeElements.forEach((el) => observer.observe(el));

// cards
document.querySelectorAll(".carro-card").forEach((card) => {
  card.addEventListener("mouseenter", () => {
    card.style.transform = "scale(1.05)";
    card.style.boxShadow = "0 10px 20px rgba(0,0,0,0.2)";
  });
  card.addEventListener("mouseleave", () => {
    card.style.transform = "scale(1)";
    card.style.boxShadow = "0 4px 6px rgba(0,0,0,0.1)";
  });
});

// setinha
const backToTop = document.createElement("button");
backToTop.textContent = "↑";
backToTop.id = "backToTop";
document.body.appendChild(backToTop);

backToTop.addEventListener("click", () =>
  window.scrollTo({ top: 0, behavior: "smooth" })
);

window.addEventListener("scroll", () => {
  backToTop.style.display = window.scrollY > 300 ? "block" : "none";
});

// mensagens automaticas
document.querySelectorAll(".flash").forEach((msg) => {
  setTimeout(() => {
    msg.style.opacity = "0";
    msg.style.transition = "opacity 0.5s ease";
  }, 3000);
});

// efeito nos inputs dos forms
document.querySelectorAll("input, textarea").forEach((input) => {
  input.addEventListener("focus", () => {
    input.style.borderColor = "#ff6600";
    input.style.boxShadow = "0 0 5px rgba(255,102,0,0.5)";
  });
  input.addEventListener("blur", () => {
    input.style.borderColor = "#ccc";
    input.style.boxShadow = "none";
  });
});

// navegaçao

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) target.scrollIntoView({ behavior: "smooth" });
  });
});

// =========================
// ABRIR E FECHAR O MODAL
// =========================

document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("checkoutModal");
    const abrirBtn = document.getElementById("abrirCheckout");

    if (abrirBtn) {
        abrirBtn.addEventListener("click", () => {
            modal.style.display = "flex";
        });
    }

    // ETAPAS DO CHECKOUT
    const etapaA = document.getElementById("etapaA");
    const etapaB = document.getElementById("etapaB");
    const etapaC = document.getElementById("etapaC");

    // Botões
    const btnToEtapaB = document.getElementById("btnToEtapaB");
    const btnToEtapaC = document.getElementById("btnToEtapaC");
    const confirmarReserva = document.getElementById("confirmarReserva");

    const voltarToA = document.getElementById("voltarToA");
    const voltarToB = document.getElementById("voltarToB");

    // Avançar para etapa B
    btnToEtapaB.addEventListener("click", () => {
        etapaA.style.display = "none";
        etapaB.style.display = "block";
    });

    // Voltar A ← B
    voltarToA.addEventListener("click", () => {
        etapaB.style.display = "none";
        etapaA.style.display = "block";
    });

    // Avançar para etapa C
    btnToEtapaC.addEventListener("click", () => {

        const metodo = document.querySelector("input[name='pagamento']:checked");

        if (!metodo) {
            alert("Selecione uma forma de pagamento.");
            return;
        }

        // PIX → Não mostra dados do cartão
        if (metodo.value === "pix") {
            document.getElementById("cartaoInfo").style.display = "none";
            document.getElementById("infoPix").style.display = "block";
        } else {
            document.getElementById("cartaoInfo").style.display = "block";
            document.getElementById("infoPix").style.display = "none";
        }

        etapaB.style.display = "none";
        etapaC.style.display = "block";
    });

    // Voltar B ← C
    voltarToB.addEventListener("click", () => {
        etapaC.style.display = "none";
        etapaB.style.display = "block";
    });

    // Finalizar reserva
    confirmarReserva.addEventListener("click", () => {
        alert("Reserva concluída com sucesso!");
        window.location.href = "/";

    });

    // SOMA DAS DIÁRIAS
    const retirada = document.getElementById("retirada");
    const devolucao = document.getElementById("devolucao");
    const precoFinal = document.getElementById("precoFinal");

    if (retirada && devolucao && precoFinal) {

        const precoBase = parseFloat(precoFinal.dataset.base);

        function calcularDias() {
            if (!retirada.value || !devolucao.value) return;

            const d1 = new Date(retirada.value);
            const d2 = new Date(devolucao.value);

            if (d2 < d1) {
                precoFinal.innerText = "0.00";
                return;
            }

            const diff = d2 - d1;
            const dias = Math.floor(diff / (1000 * 60 * 60 * 24)) + 1;
            const total = precoBase * dias;

            precoFinal.innerText = total.toFixed(2);
        }

        retirada.addEventListener("change", calcularDias);
        devolucao.addEventListener("change", calcularDias);
    }

});


// vantagens
document.addEventListener("DOMContentLoaded", () => {
  const prev = document.querySelector(".prev");
  const next = document.querySelector(".next");
  const carrossel = document.querySelector(".carrossel");

  if (prev && next && carrossel) {
    const cardWidth = 420 + 20;
    prev.addEventListener("click", () => {
      carrossel.scrollBy({ left: -cardWidth, behavior: "smooth" });
    });

    next.addEventListener("click", () => {
      carrossel.scrollBy({ left: cardWidth, behavior: "smooth" });
    });
  }
});

// ======================
// Menu de acessibilidade
// ======================
let baseFontSize = 1;

// Mostrar/ocultar menu
document.getElementById("access-btn").addEventListener("click", () => {
  const menu = document.getElementById("access-menu");
  menu.style.display = menu.style.display === "block" ? "none" : "block";
});

// AUMENTAR FONTE
function increaseFont() {
  baseFontSize += 0.2;
  document.body.style.fontSize = baseFontSize + "em";
}

// DIMINUIR FONTE
function decreaseFont() {
  baseFontSize = Math.max(0.6, baseFontSize - 0.2);
  document.body.style.fontSize = baseFontSize + "em";
}

// RESETAR FONTE
function resetFont() {
  baseFontSize = 1;
  document.body.style.fontSize = "1em";
}

// MODO ALTO CONTRASTE
function toggleContrast() {
  document.body.classList.toggle("high-contrast");
}

document.addEventListener("click", (e) => {
  const menu = document.getElementById("access-menu");
  const btn = document.getElementById("access-btn");

  if (!menu.contains(e.target) && !btn.contains(e.target)) {
    menu.style.display = "none";
  }
});
document.getElementById("abrirContato").onclick = function () {
    document.getElementById("contatoModal").style.display = "flex";
};

document.getElementById("fecharContato").onclick = function () {
    document.getElementById("contatoModal").style.display = "none";
};

window.onclick = function (e) {
    let modal = document.getElementById("contatoModal");
    if (e.target === modal) {
        modal.style.display = "none";
    }
};
