import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

function OrderDetails() {
  const { id } = useParams();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadOrderItems();
  }, []);

  const loadOrderItems = async () => {
    try {
      setLoading(true);

      const response = await axios.get(
        `http://localhost:8000/order/${id}`
      );

      setItems(response.data.items);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  // calculate total
  const total = items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  return (
    <div className="order-container">

      {/* HEADER */}
      <div className="order-header">
        <h1>Order #{id}</h1>
        <p className="order-subtitle">
          Order summary and details
        </p>
      </div>

      {/* LOADING */}
      {loading && <p>Loading order...</p>}

      {/* EMPTY STATE */}
      {!loading && items.length === 0 && (
        <div className="empty-state">
          <h3>No items found in this order</h3>
        </div>
      )}

      {/* ORDER ITEMS */}
      <div className="order-grid">

        {items.map((item, index) => (
          <div key={index} className="order-card">

            <h3 className="order-product">
              {item.product_name}
            </h3>

            <div className="order-info">
              <p>Quantity: <b>{item.quantity}</b></p>
              <p>Price: <b>Rs. {item.price}</b></p>
            </div>

            <div className="order-subtotal">
              Subtotal: Rs. {item.price * item.quantity}
            </div>

          </div>
        ))}

      </div>

      {/* SUMMARY */}
      {items.length > 0 && (
        <div className="order-summary">

          <h2>Order Summary</h2>

          <div className="summary-row">
            <span>Total Items:</span>
            <span>{items.length}</span>
          </div>

          <div className="summary-row total">
            <span>Total Amount:</span>
            <span>Rs. {total}</span>
          </div>

        </div>
      )}

    </div>
  );
}

export default OrderDetails;