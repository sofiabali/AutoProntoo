
// fade-in sessoes

const fadeElements = document.querySelectorAll('.fade-in');

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, { threshold: 0.1 });

fadeElements.forEach(el => observer.observe(el));


// cards
document.querySelectorAll('.carro-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'scale(1.05)';
        card.style.boxShadow = '0 10px 20px rgba(0,0,0,0.2)';
    });
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'scale(1)';
        card.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    });
});


// setinha
const backToTop = document.createElement('button');
backToTop.textContent = '↑';
backToTop.id = 'backToTop';
document.body.appendChild(backToTop);

backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

window.addEventListener('scroll', () => {
    backToTop.style.display = window.scrollY > 300 ? 'block' : 'none';
});


// mensagens automaticas
document.querySelectorAll('.flash').forEach(msg => {
    setTimeout(() => {
        msg.style.opacity = '0';
        msg.style.transition = 'opacity 0.5s ease';
    }, 3000);
});


// efeito nos inputs dos forms
document.querySelectorAll('input, textarea').forEach(input => {
    input.addEventListener('focus', () => {
        input.style.borderColor = '#ff6600';
        input.style.boxShadow = '0 0 5px rgba(255,102,0,0.5)';
    });
    input.addEventListener('blur', () => {
        input.style.borderColor = '#ccc';
        input.style.boxShadow = 'none';
    });
});


// navegaçao

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
});

// modal de finalizaçao
document.addEventListener('DOMContentLoaded', () => {
  const finalizarBtn = document.querySelector('.btn-finalizar');
  const modal = document.getElementById('checkoutModal');
  const cancelBtn = document.getElementById('cancelBtn');
  const checkoutForm = document.getElementById('checkoutForm');

  if (!finalizarBtn || !modal || !cancelBtn || !checkoutForm) return;

  finalizarBtn.addEventListener('click', () => {
    modal.style.display = 'flex';
  });

  cancelBtn.addEventListener('click', () => {
    modal.style.display = 'none';
  });

  checkoutForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(checkoutForm);

    try {
      const response = await fetch('/finalizar_reserva', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        alert('Reserva finalizada com sucesso! Verifique seu email. 📧');
        window.location.href = '/carros';
      } else {
        alert('Erro ao finalizar a reserva.');
      }
    } catch (error) {
      console.error(error);
      alert('Erro na requisição.');
    }
  });
});

  // vantagens
document.addEventListener('DOMContentLoaded', () => {
  const prev = document.querySelector('.prev');
  const next = document.querySelector('.next');
  const carrossel = document.querySelector('.carrossel');

  if (prev && next && carrossel) {
    const cardWidth = 420 + 20; 
    prev.addEventListener('click', () => {
      carrossel.scrollBy({ left: -cardWidth, behavior: 'smooth' });
    });

    next.addEventListener('click', () => {
      carrossel.scrollBy({ left: cardWidth, behavior: 'smooth' });
    });
  }
});

// soma das diarias
document.addEventListener("DOMContentLoaded", () => {
    const retirada = document.getElementById("retirada");
    const devolucao = document.getElementById("devoluçao");
    const precoFinal = document.getElementById("precoFinal");

    const precoBase = parseFloat(precoFinal.innerText); 

    function calcularDias() {
        if (!retirada.value || !devolucao.value) return;

        const data1 = new Date(retirada.value);
        const data2 = new Date(devolucao.value);

        if (data2 < data1) {
            precoFinal.innerText = "0.00";
            return;
        }

        let diff = data2 - data1;

        let dias = Math.floor(diff / (1000 * 60 * 60 * 24)) + 1;  

        let total = precoBase * dias;

        precoFinal.innerText = total.toFixed(2);
    }

    retirada.addEventListener("change", calcularDias);
    devolucao.addEventListener("change", calcularDias);
});


