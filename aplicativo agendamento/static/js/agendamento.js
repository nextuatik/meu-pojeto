const form = document.getElementById('formAgendamento');
const barbeiro = document.getElementById('barbeiro');
const data = document.getElementById('data');
const hora = document.getElementById('hora');

// Atualiza horários dinamicamente
function atualizarHorarios() {
    const b = barbeiro.value;
    const d = data.value;

    if (!b || !d) {
        hora.innerHTML = '<option value="">Escolha barbeiro e data</option>';
        return;
    }

    fetch(`/horarios_disponiveis?barbeiro=${b}&data=${d}`)
        .then(res => res.json())
        .then(lista => {
            hora.innerHTML = '';
            if (lista.length === 0) {
                hora.innerHTML = '<option value="">Sem horários disponíveis</option>';
            } else {
                lista.forEach(h => {
                    hora.innerHTML += `<option value="${h}">${h}</option>`;
                });
            }
        })
        .catch(err => {
            hora.innerHTML = '<option value="">Erro ao carregar horários</option>';
            console.error(err);
        });
}

barbeiro.addEventListener('change', atualizarHorarios);
data.addEventListener('change', atualizarHorarios);

// Envia formulário via fetch + SweetAlert2
form.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(form);

    fetch('/enviar', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.sucesso === "1") {
            Swal.fire({
                icon: 'success',
                title: '✅ Agendamento confirmado!',
                text: 'Seu horário foi reservado com sucesso.'
            });
            form.reset();
            hora.innerHTML = '<option value="">Escolha barbeiro e data</option>';
        } else {
            Swal.fire({
                icon: 'error',
                title: '⚠ Horário já ocupado!',
                text: 'Escolha outro horário, por favor.'
            });
        }
    })
    .catch(err => {
        Swal.fire({
            icon: 'error',
            title: 'Erro!',
            text: 'Não foi possível enviar o agendamento.'
        });
        console.error(err);
    });
});
