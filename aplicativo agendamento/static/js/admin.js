// Alternar abas
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// Filtro de busca
const busca = document.getElementById("busca");
if (busca) {
  busca.addEventListener("keyup", function() {
    let filtro = busca.value.toLowerCase();
    document.querySelectorAll("#tabelaHorarios tbody tr").forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(filtro) ? "" : "none";
    });
  });
}

// Confirmação de exclusão com SweetAlert
function confirmarExclusao(id) {
  Swal.fire({
    title: 'Tem certeza?',
    text: "Essa ação não pode ser desfeita!",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#555',
    confirmButtonText: 'Sim, excluir!'
  }).then((result) => {
    if (result.isConfirmed) {
      window.location.href = `/admin/excluir_horario/${id}`;
    }
  });
}
