document.getElementById('verificationForm').addEventListener('submit', function(event) {
  event.preventDefault();
  const email = document.getElementById('emailVerification').value;

  fetch('http://44.221.194.95:5000/verifyUserEmail', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: email,
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

  alert(`Verification email sent to ${email}.`);
});

function getUrlParameter(name) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
}

if (window.location.pathname.includes('verification.html')) {
  const emailParam = getUrlParameter('email');
  if (emailParam) {
      document.getElementById('emailVerification').value = emailParam;
  }
}
