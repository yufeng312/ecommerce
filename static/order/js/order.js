// 订单取消页 -- 定时器逻辑
const countdownElement = document.getElementById('countdown');
if (countdownElement) {
    let timeLeft = 5;
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
}

// 确认订单页 -- 地址选择框逻辑
document.addEventListener('DOMContentLoaded', function () {
    const confirmBtn = document.getElementById('confirm-address-btn');
    const hiddenInput = document.getElementById('selected-address-id');
    const displayName = document.getElementById('display-receiver-name');
    const displayPhone = document.getElementById('display-receiver-phone');
    const displayAddress = document.getElementById('display-receiver-address');
    const addressModalElement = document.getElementById('addressModal');
    if (confirmBtn && addressModalElement) {
    confirmBtn.addEventListener('click', function () {
        const selectedRadio = document.querySelector('input[name="modal_address_choice"]:checked');
        if (selectedRadio) {
            const addressId = selectedRadio.value;
            const name = selectedRadio.dataset.name;
            const phone = selectedRadio.dataset.phone;
            const address = selectedRadio.dataset.address;
            if (hiddenInput) {
                hiddenInput.value = addressId;
            }
            if (displayName) displayName.textContent = name;
            if (displayPhone) displayPhone.textContent = phone;
            if (displayAddress) displayAddress.textContent = address;
            const modalInstance = bootstrap.Modal.getInstance(addressModalElement);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
    });
    }
});