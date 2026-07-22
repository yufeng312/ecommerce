document.addEventListener('DOMContentLoaded', function () {
    const btnPlusList = document.querySelectorAll('.btn-plus');
    const btnMinusList = document.querySelectorAll('.btn-minus');

    // 点击加号,数量加1
    btnPlusList.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const inputQuantity = btn.parentElement.querySelector('.quantity-input');
            let currentValue = parseInt(inputQuantity.value) || 1;
            inputQuantity.value = currentValue + 1;
            updateBasket(inputQuantity);
        });
    });

    // 点击减号,数量减1
    btnMinusList.forEach(function (btn) {
        btn.addEventListener('click', function (event) {
            const inputQuantity = btn.parentElement.querySelector('.quantity-input');
            let currentValue = parseInt(inputQuantity.value) || 1;
            if (currentValue > 1) {
                inputQuantity.value = currentValue - 1;
                updateBasket(inputQuantity);
            }
        });
    });

    // 输入框直接修改
    const inputList = document.querySelectorAll('.quantity-input')
    inputList.forEach(function (input) {
        input.addEventListener('change', function () {
            let currentValue = parseInt(input.value);
            if (isNaN(currentValue) || currentValue < 1) {
                input.value = 1;
            }
            updateBasket(input);
        });
    });

    // 更新购物车页和session中商品数量函数
    function updateBasket (input) {
        const productItem = input.closest('.product-item');

        const productId = productItem.getAttribute('data-index');
        const priceText = productItem.querySelector('.product-price').innerText;
        const price = parseFloat(priceText.replace('¥', '')) || 0;
        const qty = parseInt(input.value) || 1;

        // 单个商品合计金额
        const subtotal = price * qty;
        const subtotalElement = productItem.querySelector(`#subtotal-${productId}`);  // 动态拼接
        subtotalElement.innerText = '¥' + subtotal.toFixed(2);  // 保留两位小数

        // 异步向basket_update视图发送商品id和数量
        const urlUpdate = productItem.getAttribute('data-url');
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        fetch(urlUpdate, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                product_id: productId,
                product_qty: qty
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('购物车更新成功');
                // 更新商品总价
                calculateTotalPrice();
            } else {
                console.log('购物车更新失败: ' + data.message);
            }
        })
        .catch(error => {
            console.log('网络请求异常', error);
        });
    }

    // 删除按钮
    const btnDeleteList = document.querySelectorAll('.delete-button');
    btnDeleteList.forEach(function (btn) {
        btn.addEventListener('click',async function (event) {
            event.preventDefault();

            // 确认删除弹窗
            if(!confirm('确定要删除这件商品吗?')) return;

            const urlDelete = btn.getAttribute('data-url');
            const productId = btn.getAttribute('data-index');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            try {
                const response = await fetch (urlDelete, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        'product_id': productId
                    })
                })
                const data = await response.json();
                if (data && data.status === 'success') {
                    const removeItem = btn.closest('.product-item');
                    if (removeItem) {
                        removeItem.remove();
                        const categoryCount = document.getElementById('basket-qty-summary');
                        if (categoryCount) {
                            categoryCount.innerText = data.category_count + ' 种';
                        }
                        if (data.category_count === 0) {
                            const contentWrapper = document.getElementById('basket-content-wrapper');
                            const emptyWrapper = document.getElementById('basket-empty-wrapper');

                            contentWrapper.classList.add('d-none');
                            emptyWrapper.classList.remove('d-none');
                        }
                    }
                    calculateTotalPrice();
                }
            } catch (error) {
                console.log(error)
            }
        })
    });

    // 更新商品总价
    function calculateTotalPrice() {
        // 全部商品总金额
        let totalAll = 0;
        document.querySelectorAll('.product-item').forEach(item => {
            const itemPriceText = item.querySelector('.product-price').innerText;
            const itemPrice = parseFloat(itemPriceText.replace('¥', '')) || 0;
            const itemQty = parseInt(item.querySelector('.quantity-input').value);
            totalAll += itemPrice * itemQty;
        });

        // 更新总金额,保留2位小数
        const totalPriceElement = document.getElementById('total-price');
        if (totalPriceElement) {
        totalPriceElement.innerText = '¥' + totalAll.toFixed(2);
        }
        const feightPrice = document.getElementById('freight')
        if (totalAll >= 99) {
            feightPrice.innerText = '包邮'
        } else {
            feightPrice.innerText = '¥10.00'
        }
    }

    // 更新购物车商品数量
});