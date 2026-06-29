// 加入购物车按钮逻辑
document.addEventListener('DOMContentLoaded',function(){
    const basketBtn = document.getElementById('add-button');

    if (basketBtn) {

        // 异步点击事件
        basketBtn.addEventListener('click', async function (event) {

            // 阻止按钮刷新表单
            event.preventDefault();

            const url = this.getAttribute('data-url');
            const productId = this.getAttribute('value');
            const productQty = document.getElementById('inputQuantity').value;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            
            try {

                // 异步等待数据发送到后端,接收返回的响应
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',  // 发送json类型的数据
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({product_id: productId, product_qty: productQty})
                });

                const data = await response.json()
                if (data) {
                    document.getElementById('basket-qty').innerHTML = data.qty
                }
            } catch (error) {
                console.error(error);
            }
        });
    }
});


// 商品详情页数量加减逻辑
document.addEventListener('DOMContentLoaded', function () {
    const inputQuantity = document.getElementById('inputQuantity')
    const btnPlus = document.getElementById('btnPlus')
    const btnMinus = document.getElementById('btnMinus')

    // 点击加号
    btnPlus.addEventListener('click', function () {
        let currentValue = parseInt(inputQuantity.value) || 1;
        inputQuantity.value = currentValue + 1;
    });

    // 点击建号
    btnMinus.addEventListener('click', function () {
        let currentValue = parseInt(inputQuantity.value) || 1;
        if (inputQuantity.value > 1) {
        inputQuantity.value = currentValue - 1;
        }
    });

    // 防止输入负数或者空值
    inputQuantity.addEventListener('change', function () {
        let currentValue = parseInt(inputQuantity.value);
        if (isNaN(currentValue) || currentValue < 1) {
            inputQuantity.value = 1;
        }
    });
});