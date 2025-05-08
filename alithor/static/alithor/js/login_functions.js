// login_functions.js

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$(document).ready(function () {
  $('#loginForm').submit(function (e) {
    e.preventDefault();

    $.ajax({
      url: LOGIN_URL, // 🔁 Pasado desde el HTML
      type: 'POST',
      headers: { 'X-CSRFToken': csrftoken },
      data: {
        username: $('#usuario').val(),
        password: $('#contrasena').val()
      },
      success: function (response) {
        if (response.success) {
          Swal.fire({
            icon: 'success',
            title: '¡Bienvenido!',
            text: 'Redirigiendo al panel...',
            showConfirmButton: false,
            timer: 1500
          }).then(() => {
            window.location.href = response.redirect_url;
          });
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Credenciales incorrectas',
            text: response.error
          });
        }
      },
      error: function () {
        Swal.fire({
          icon: 'error',
          title: 'Error de servidor',
          text: 'Ocurrió un problema al intentar iniciar sesión.'
        });
      }
    });
  });
});
