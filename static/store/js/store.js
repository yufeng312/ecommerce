// 加入购物车按钮逻辑
document.addEventListener('DOMContentLoaded',function(){
    // 监听全局点击事件
    const addBasketList = document.querySelectorAll('.add-basket-btn, #add-button');

    addBasketList.forEach(function (btn){
        btn.addEventListener('click', async function (event) {
            // 阻止按钮刷新表单
            event.preventDefault();

            const url = btn.getAttribute('data-url');
            const productId = btn.getAttribute('data-index');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            let productQty = 1;
            const LocalQtyInput = document.getElementById('inputQuantity');
            if (LocalQtyInput) {
                productQty = parseInt(LocalQtyInput.value) || 1;
            }
    
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
                console.log(error);
            }
        });
    });  
});

// 商品详情页数量加减逻辑
document.addEventListener('DOMContentLoaded', function () {
    const inputQuantity = document.getElementById('inputQuantity')
    const btnPlus = document.getElementById('btnPlus')
    const btnMinus = document.getElementById('btnMinus')

    // 点击加号
    if (btnPlus) {
        btnPlus.addEventListener('click', function () {
            let currentValue = parseInt(inputQuantity.value) || 1;
            inputQuantity.value = currentValue + 1;
        });
    };

    // 点击减号
    if (btnMinus) {
        btnMinus.addEventListener('click', function () {
            let currentValue = parseInt(inputQuantity.value) || 1;
            if (currentValue > 1) {
            inputQuantity.value = currentValue - 1;
            }
        });
    }

    // 防止输入负数或者空值
    if (inputQuantity) {
        inputQuantity.addEventListener('change', function () {
            let currentValue = parseInt(inputQuantity.value);
            if (isNaN(currentValue) || currentValue < 1) {
                inputQuantity.value = 1;
            }
        });
    }
});

// 商品详情页图片切换逻辑
document.addEventListener('DOMContentLoaded', function () {
  const mainImg = document.getElementById('mainProductImage');
  const thumbs = document.querySelectorAll('.product-thumb');
  if (mainImg && thumbs.length > 0) {
    thumbs.forEach(thumb => {
      thumb.addEventListener('click', function () {
        mainImg.style.opacity = '0.5';
        setTimeout(() => {
          mainImg.src = this.src;
          mainImg.style.opacity = '1';
        }, 150);
        thumbs.forEach(t => {
          t.classList.remove('border-primary', 'border-2', 'opacity-100');
          t.classList.add('opacity-75');
        });
        this.classList.add('border-primary', 'border-2', 'opacity-100');
        this.classList.remove('opacity-75');
      });
    });
  }
});