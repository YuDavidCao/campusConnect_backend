document.getElementById('resetForm').addEventListener('submit', function (event) {
  event.preventDefault();
  const email = document.getElementById('email').value;
  const token = getUrlParameter('token')
  const uid = getUrlParameter('uid')
  const newPassword = document.getElementById('newPassword').value;
  console.log(email
    , token
    , uid
    , newPassword
  );
  fetch('http://44.221.194.95:5000/resetPassword', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: email,
      token: token,
      newPassword: newPassword,
      uid: uid
    })
  })
    .then(response => {
      if (response.ok) {
        return "";
      }
      throw new Error('Network response was not ok.');
    })
    .then(data => {
      alert(`Password reset successful`);
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Failed to reset password.');
    });
});

function getUrlParameter(name) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
}

// Populate the email field on password reset page from URL parameter
if (window.location.pathname.includes('reset.html')) {
  const emailParam = getUrlParameter('email');
  if (emailParam) {
    document.getElementById('email').value = emailParam;
  }
}