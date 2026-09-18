import { useEffect, useState } from "react";
import axios from "axios";


function Cart() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);

  const user = JSON.parse(
    localStorage.getItem("user")
  );

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    const response = await axios.get(
      `http://localhost:8000/cart/${user.id}`
    );

    setItems(response.data.items);
    setTotal(response.data.total);
  };

  const removeItem = async (cartId) => {
    await axios.delete(
      `http://localhost:8000/cart/remove/${cartId}`
    );

    loadCart();
  };

  const clearCart = async () => {
    await axios.delete(
      `http://localhost:8000/cart/clear/${user.id}`
    );

    loadCart();
  };

  return (
    <div className="container">

      <header className="cart-header">
        <h1 className="cart-title">
          Your Cart
        </h1>

        <span className="cart-meta">
          You have {items.length} item{items.length !== 1 ? "s" : ""} in your shopping cart
        </span>
      </header>

      {items.length === 0 ? (

        <div className="empty-cart">
          <h2>Cart is Empty</h2>
          <p>Add some products to your cart.</p>
        </div>

      ) : (

        <main className="cart-layout">

          <section className="cart-items-list">

            {items.map((item) => (

              <div
                key={item.cart_id}
                className="cart-item"
              >

                <div className="item-img-wrap">
                  <img
                    src={item.image}
                    alt={item.name}
                  />
                </div>

                <div className="item-details">

                  <h3 className="item-name">
                    {item.name}
                  </h3>

                  <span className="item-size">
                    Size: <strong>{item.size}</strong>
                  </span>

                  <button
                    className="btn-remove-item"
                    onClick={() =>
                      removeItem(item.cart_id)
                    }
                  >
                    Remove
                  </button>

                </div>

                {/* UI Only (No Backend Change) */}
                <div className="quantity-control">

                  <button
                    className="qty-btn"
                    disabled
                  >
                    −
                  </button>

                  <span className="qty-val">
                    {item.quantity}
                  </span>

                  <button
                    className="qty-btn"
                    disabled
                  >
                    +
                  </button>

                </div>

                <div className="cart-item-price">
                  Rs. {item.price}
                </div>

              </div>

            ))}

          </section>

          <aside className="cart-summary">

            <h2 className="summary-title">
              Order Summary
            </h2>

            <div className="summary-row">
              <span>Subtotal</span>
              <span>Rs. {total}</span>
            </div>

            <div className="summary-row">
              <span>Shipping</span>
              <span>Free</span>
            </div>

            <div className="summary-row">
              <span>Estimated Tax</span>
              <span>Calculated at checkout</span>
            </div>

            <div className="summary-row total">
              <span>Total</span>
              <span>Rs. {total}</span>
            </div>

            <div className="summary-actions">

              <button
                className="btn-checkout"
                onClick={() =>
                  window.location.href = "/checkout"
                }
              >
                Proceed to Checkout
              </button>

              <button
                className="btn-clear-cart"
                onClick={clearCart}
              >
                Clear Entire Cart
              </button>

            </div>

            <a
              href="/"
              className="back-to-shop"
            >
              ← Continue Shopping
            </a>

          </aside>

        </main>

      )}

    </div>
  );
}

export default Cart;