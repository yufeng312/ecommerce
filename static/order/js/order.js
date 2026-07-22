let timeLeft = 5;
const countdownElement = document.getElementById('countdown');

const timer = setInterval(() => {
timeLeft--;
countdownElement.innerText = timeLeft;

if (timeLeft <= 0) {
    clearInterval(timer);
    window.location.href = "{% url 'store:index' %}";
}
}, 1000);