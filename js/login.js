document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');

  const loginAlert = document.getElementById('login-alert');
  const registerAlert = document.getElementById('register-alert');

  function showAlert(alertElement, message, isSuccess = false) {
    alertElement.textContent = message;
    alertElement.style.display = 'block';
    if (isSuccess) {
      alertElement.style.color = '#a3e635'; // Light green
      alertElement.style.borderColor = '#84cc16';
      alertElement.style.background = 'rgba(132, 204, 22, 0.15)';
    } else {
      alertElement.style.color = '#ff8787'; // Light red
      alertElement.style.borderColor = '#ff652f';
      alertElement.style.background = 'rgba(255, 101, 47, 0.15)';
    }
  }

  function hideAlert(alertElement) {
    alertElement.style.display = 'none';
    alertElement.textContent = '';
  }

  // Handle Login
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert(loginAlert);

      const usernameInput = document.getElementById('loginUser');
      const passwordInput = document.getElementById('loginPassword');

      const username = usernameInput.value.trim();
      const password = passwordInput.value;

      if (!username || !password) {
        showAlert(loginAlert, 'Username dan password tidak boleh kosong.');
        return;
      }

      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ username, password })
        });

        const result = await response.json();

        if (response.ok && result.success) {
          showAlert(loginAlert, 'Login berhasil! Mengalihkan...', true);
          // Simpan session lokal
          localStorage.setItem('currentUser', username);
          setTimeout(() => {
            window.location.href = 'mainsweeper.html';
          }, 1000);
        } else {
          showAlert(loginAlert, result.message || 'Login gagal.');
        }
      } catch (err) {
        console.error(err);
        showAlert(loginAlert, 'Koneksi ke server gagal. Pastikan server lokal berjalan.');
      }
    });
  }

  // Handle Register
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert(registerAlert);

      const usernameInput = document.getElementById('username');
      const passwordInput = document.getElementById('password');
      const confirmPasswordInput = document.getElementById('confirmPassword');

      const username = usernameInput.value.trim();
      const password = passwordInput.value;
      const confirmPassword = confirmPasswordInput.value;

      // Client-side validations
      if (username.length < 3) {
        showAlert(registerAlert, 'Username minimal 3 karakter.');
        return;
      }

      if (password.length < 6) {
        showAlert(registerAlert, 'Password minimal 6 karakter.');
        return;
      }

      if (password !== confirmPassword) {
        showAlert(registerAlert, 'Konfirmasi password tidak cocok.');
        return;
      }

      try {
        const response = await fetch('/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ username, password })
        });

        const result = await response.json();

        if (response.ok && result.success) {
          showAlert(registerAlert, result.message || 'Registrasi berhasil!', true);
          // Kosongkan form input
          usernameInput.value = '';
          passwordInput.value = '';
          confirmPasswordInput.value = '';

          // Setelah sejenak, tutup popup register dan arahkan ke login
          setTimeout(() => {
            window.location.hash = ''; // Clear hash to hide the popup
            hideAlert(registerAlert);
          }, 2000);
        } else {
          showAlert(registerAlert, result.message || 'Registrasi gagal.');
        }
      } catch (err) {
        console.error(err);
        showAlert(registerAlert, 'Koneksi ke server gagal. Pastikan server lokal berjalan.');
      }
    });
  }
});
