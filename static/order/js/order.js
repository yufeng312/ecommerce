let timeLeft = 5;
const countdownElement = document.getElementById('countdown');
const redirectUrl = countdownElement.dataset.url; 

const timer = setInterval(() => {
  timeLeft--;
  if (countdownElement) {
    countdownElement.innerText = timeLeft;
  }

  if (timeLeft <= 0) {
    clearInterval(timer);
    window.location.href = redirectUrl; 
  }
}, 1000);