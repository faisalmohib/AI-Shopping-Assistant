import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

function Orders() {

  const [orders, setOrders] = useState([]);

  const user = JSON.parse(
    localStorage.getItem("user")
  );

  useEffect(() => {

    loadOrders();

  }, []);

  const loadOrders = async () => {

    try {

      const response = await axios.get(
        `http://localhost:8000/orders/${user.id}`
      );

      setOrders(response.data);

    } catch (error) {

      console.log(error);

    }
  };

  return (

    <div className="orders-page">

      <h1>My Orders</h1>

      {
        orders.length === 0
          ? (
            <h3>No Orders Found</h3>
          )
          : (
            orders.map((order) => (

              <div
                key={order.id}
                className="order-card"
              >

                <h3>
                  Order #{order.id}
                </h3>

                <p>
                  Total:
                  Rs. {order.total_amount}
                </p>

                <p>
                  Date:
                  {order.created_at}
                </p>

                <Link
                  to={`/order/${order.id}`}
                >
                  View Details
                </Link>

              </div>

            ))
          )
      }

    </div>

  );
}

export default Orders;