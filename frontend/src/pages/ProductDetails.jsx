import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";

import axios from "axios";

function ProductDetails() {

  const { id } = useParams();

  const navigate = useNavigate();

  const [product, setProduct] = useState(null);

  const [sizes, setSizes] = useState([]);

  const [selectedSize, setSelectedSize] = useState("");

  const [loadingBuy, setLoadingBuy] = useState(false);

  // ⭐ AI Description
  const [description, setDescription] = useState("");

  const [loadingDescription, setLoadingDescription] = useState(false);

   // AI Recomendation
  const [recommended, setRecommended] = useState([]);
  const [loadingRec, setLoadingRec] = useState(false);

  const user = JSON.parse(
    localStorage.getItem("user")
  );

  useEffect(() => {

    loadProduct();

    loadSizes();

  }, [id]);

  const loadProduct = async () => {

    try {

      const response =
        await axios.get(
          `http://localhost:8000/product/${id}`
        );

      setProduct(response.data);

      // Generate AI description
      loadDescription(response.data);
      // recomendation call
      loadRecommendations(response.data.id);

      // Save Recently Viewed
      if (user) {

        await axios.post(
          "http://localhost:8000/recently-viewed/add",
          {
            user_id: user.id,
            product_id: id
          }
        );

      }

    } catch (error) {

      console.log(error);

      alert("Failed to load product");

    }

  };

  const loadDescription = async (productData) => {

    try {

      setLoadingDescription(true);

      const response =
        await axios.post(
          "http://localhost:8000/product/description",
          {
            product: productData
          }
        );

      setDescription(
        response.data.description
      );

    } catch (error) {

      console.log(error);

      setDescription(
        "AI description not available."
      );

    } finally {

      setLoadingDescription(false);

    }

  };

  const loadRecommendations = async (productId) => {

  try {

    setLoadingRec(true);

    const response = await axios.get(
      `http://localhost:8000/recommend/${productId}`
    );

    setRecommended(response.data.products);

  } catch (error) {

    console.log(error);

  } finally {

    setLoadingRec(false);
  }
 };

  const loadSizes = async () => {

    try {

      const response =
        await axios.get(
          `http://localhost:8000/product/${id}/sizes`
        );

      setSizes(response.data);

    } catch (error) {

      console.log(error);

    }

  };

  const addToCart = async () => {

    if (!user) {

      navigate("/login");

      return;

    }

    if (!selectedSize) {

      alert("Please select a size");

      return;

    }

    try {

      await axios.post(
        "http://localhost:8000/cart/add",
        {
          user_id: user.id,
          product_id: product.id,
          size: selectedSize,
          quantity: 1
        }
      );

      alert("Added To Cart");

    } catch (error) {

      console.log(error);

      alert("Failed");

    }

  };

  const addToWishlist = async () => {

    if (!user) {

      navigate("/login");

      return;

    }

    try {

      const response =
        await axios.post(
          "http://localhost:8000/wishlist/add",
          {
            user_id: user.id,
            product_id: product.id
          }
        );

      alert(response.data.message);

    } catch (error) {

      console.log(error);

      alert("Failed to add to wishlist");

    }

  };

  const directBuy = async () => {

    if (!user) {

      navigate("/login");

      return;

    }

    try {

      setLoadingBuy(true);

      const response =
        await axios.post(
          "http://localhost:8000/direct-buy",
          {
            user_id: user.id,
            product_id: product.id,
            product_name: product.name,
            price: product.price,
            quantity: 1,

            phone: "03000000000",
            address: "IIUI H-10 Islamabad",

            card_number: "4111111111111111",
            expiry: "12/30",
            cvv: "123"
          }
        );

      if (response.data.success) {

        alert(
          `Order placed successfully #${response.data.order_id}`
        );

        navigate("/orders");

      }

    } catch (error) {

      console.log(error);

      alert("Direct Buy Failed");

    } finally {

      setLoadingBuy(false);

    }

  };

  if (!product)
    return <h2>Loading...</h2>;

  return (
  <div className="container">

    <main className="product-container">

      {/* IMAGE SIDE */}
      <div className="product-image-side">
        <img src={product.image} alt={product.name} />
      </div>

      {/* DETAILS SIDE */}
      <div className="product-details-side">

        <h1 className="product-name">{product.name}</h1>

        {/* AI DESCRIPTION (optional keep) */}
        <h3>Description</h3>
        {loadingDescription ? (
          <p>Generating AI description...</p>
        ) : (
          <p className="product-description">{description}</p>
        )}

        {/* SIZE SECTION */}
        <div className="size-section">
          <h3 className="size-title">Select Size</h3>

          <div className="size-options">
            {sizes.filter(s => s.available === 1).map(size => (
              <button
                key={size.size}
                className={`size-btn ${selectedSize === size.size ? "active" : ""}`}
                onClick={() => setSelectedSize(size.size)}
              >
                {size.size}
              </button>
            ))}
          </div>
        </div>

        {/* ACTION BUTTONS */}
        <div className="action-buttons">

          <div className="btn-row">

            <button className="btn btn-add-cart" onClick={addToCart}>
              Add to Cart
            </button>

            <button className="btn btn-wishlist" onClick={addToWishlist}>
              ❤️ Wishlist
            </button>

          </div>

          <button
            className="btn btn-buy"
            onClick={() => {
              if (!selectedSize) return alert("Select size first");
              navigate(`/checkout/${product.id}?size=${selectedSize}`);
            }}
          >
            Buy Now
          </button>

          <button className="btn btn-direct-buy" onClick={directBuy} disabled={loadingBuy}>
            {loadingBuy ? "Processing..." : "Direct Express Buy"}
          </button>

        </div>

      </div>
    </main>

    {/* ===================== */}
    {/* RECOMMENDATION SECTION */}
    {/* ===================== */}

    <section className="related-section">

      <h2 className="related-title">You May Also Like</h2>

      {loadingRec ? (
        <p>Loading recommendations...</p>
      ) : (
        <div className="related-grid">

          {recommended.map(item => (
            <div
              key={item.id}
              className="product-card"
              onClick={() => navigate(`/product/${item.id}`)}
            >

              <div className="card-img-wrap">
                <img src={item.image} alt={item.name} />
              </div>

              <h3 className="card-title">{item.name}</h3>

              <p className="card-price">Rs. {item.price}</p>

            </div>
          ))}

        </div>
      )}

    </section>

  </div>
);

}

export default ProductDetails;