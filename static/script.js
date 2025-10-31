
// FADE-IN DAS SEÇÕES

const fadeElements = document.querySelectorAll('.fade-in');

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, { threshold: 0.1 });

fadeElements.forEach(el => observer.observe(el));


// INTERAÇÃO NOS CARDS DE VEÍCULOS
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


// BOTÃO VOLTAR AO TOPO
const backToTop = document.createElement('button');
backToTop.textContent = '↑';
backToTop.id = 'backToTop';
document.body.appendChild(backToTop);

backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

window.addEventListener('scroll', () => {
    backToTop.style.display = window.scrollY > 300 ? 'block' : 'none';
});


// FLASH MESSAGES AUTOMÁTICAS
document.querySelectorAll('.flash').forEach(msg => {
    setTimeout(() => {
        msg.style.opacity = '0';
        msg.style.transition = 'opacity 0.5s ease';
    }, 3000);
});


// EFEITO NOS INPUTS DE FORMULÁRIO
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


// NAVEGAÇÃO SUAVE (SMOOTH SCROLL)

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
});

// ====== MODAL DE FINALIZAÇÃO ======
document.addEventListener('DOMContentLoaded', () => {
  const finalizarBtn = document.querySelector('.btn-finalizar');
  const modal = document.getElementById('confirmModal');
  if (!finalizarBtn || !modal) return;

  const confirmBtn = document.getElementById('confirmBtn');
  const cancelBtn = document.getElementById('cancelBtn');

  finalizarBtn.addEventListener('click', () => modal.style.display = 'flex');
  cancelBtn.addEventListener('click', () => modal.style.display = 'none');

  confirmBtn.addEventListener('click', async () => {
    await fetch('/remover_todos');
    modal.style.display = 'none';
    alert('Reserva finalizada com sucesso! 🚗');
    window.location.href = '/carros';
  });
});
