import { useState, useEffect } from "react";
import axios from "axios";
import {
  useNavigate,
  useParams,
  useSearchParams
} from "react-router-dom";

function Checkout() {

  const { id } = useParams();

  const [searchParams] = useSearchParams();

  const selectedSize =
    searchParams.get("size");

  const navigate = useNavigate();

  const [product, setProduct] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const user = JSON.parse(
    localStorage.getItem("user")
  );

  const [customerName,
    setCustomerName] = useState(
      user?.full_name || ""
    );

  const [phone,
    setPhone] = useState("");

  const [address,
    setAddress] = useState("");

  const [paymentMethod,
    setPaymentMethod] = useState(
      "Cash On Delivery"
    );

  const [cardNumber,
    setCardNumber] = useState("");

  const [expiry,
    setExpiry] = useState("");

  const [cvv,
    setCvv] = useState("");

  useEffect(() => {

    // Cart Checkout
    if (!id) {

      setLoading(false);
      return;

    }

    // Buy Now
    const loadProduct = async () => {

      try {

        const response =
          await axios.get(
            `http://localhost:8000/product/${id}`
          );

        setProduct(response.data);

      } catch (error) {

        console.log(error);

        alert("Product not found");

      } finally {

        setLoading(false);

      }

    };

    loadProduct();

  }, [id]);

  const placeOrder = async () => {

    if (!user) {

      navigate("/login");
      return;

    }

    if (!phone || !address) {

      alert(
        "Please fill all required fields"
      );

      return;

    }

    if (paymentMethod === "Card") {

      if (
        !cardNumber ||
        !expiry ||
        !cvv
      ) {

        alert(
          "Please fill card details"
        );

        return;

      }

    }

    try {

      const response =
        await axios.post(
          "http://localhost:8000/checkout",
          {

            user_id: user.id,

            customer_name:
              customerName,

            phone,

            address,

            payment_method:
              paymentMethod,

            card_number:
              cardNumber,

            expiry,

            cvv,

            // Buy Now only
            ...(id && {

              product_id: Number(id),

              quantity: 1,

              selected_size:
                selectedSize

            })

          }
        );

      if (
        response.data.success
      ) {

        alert(
          `Order #${response.data.order_id} placed successfully`
        );

        navigate("/orders");

      }

      else {

        alert(
          response.data.message
        );

      }

    } catch (error) {

      console.log(error);

      alert(
        "Failed to place order"
      );

    }

  };

  if (loading) {

    return <h2>Loading...</h2>;

  }

  if (id && !product) {

    return (
      <h2>
        Product not found.
      </h2>
    );

  }

  return (

    <div className="checkout-page">

      <h1>
        Checkout
      </h1>

      {/* Buy Now Product */}

      {id && product && (

        <div className="checkout-product">

          <img
            src={product.image}
            alt={product.name}
            width="250"
          />

          <h2>
            {product.name}
          </h2>

          <h3>
            Rs. {product.price}
          </h3>

          <p>
            <strong>
              Brand:
            </strong>{" "}
            {product.brand}
          </p>

          <p>
            <strong>
              Color:
            </strong>{" "}
            {product.color}
          </p>

          <h3>
            Selected Size:{" "}
            {selectedSize ||
              "Not Selected"}
          </h3>

        </div>

      )}

      <input
        type="text"
        value={customerName}
        onChange={(e) =>
          setCustomerName(
            e.target.value
          )
        }
        placeholder="Full Name"
      />

      <input
        type="text"
        value={phone}
        onChange={(e) =>
          setPhone(
            e.target.value
          )
        }
        placeholder="Phone Number"
      />

      <textarea
        value={address}
        onChange={(e) =>
          setAddress(
            e.target.value
          )
        }
        placeholder="Delivery Address"
      />

      <h3>
        Payment Method
      </h3>

      <select
        value={paymentMethod}
        onChange={(e) =>
          setPaymentMethod(
            e.target.value
          )
        }
      >

        <option>
          Cash On Delivery
        </option>

        <option>
          Card
        </option>

        <option>
          EasyPaisa
        </option>

        <option>
          JazzCash
        </option>

      </select>

      {paymentMethod ===
        "Card" && (

        <>

          <input
            type="password"
            value={cardNumber}
            onChange={(e) =>
              setCardNumber(
                e.target.value
              )
            }
            placeholder="Card Number"
          />

          <input
            type="text"
            value={expiry}
            onChange={(e) =>
              setExpiry(
                e.target.value
              )
            }
            placeholder="Expiry MM/YY"
          />

          <input
            type="password"
            value={cvv}
            onChange={(e) =>
              setCvv(
                e.target.value
              )
            }
            placeholder="CVV"
          />

        </>

      )}

      <button
        onClick={placeOrder}
      >
        Place Order
      </button>

    </div>

  );

}

export default Checkout;