import { Link } from "react-router-dom";
import axios from "axios";

function ProductCard({ product }) {

  const user = JSON.parse(
    localStorage.getItem("user")
  );


  // ======================
  // Add to Wishlist
  // ======================
  const addToWishlist = async () => {

    try {

      const response = await axios.post(
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

  return (

    <div className="product-card">

      <img
        src={product.image}
        alt={product.name}
        className="product-image"
      />

      <div className="product-content">

        <h3>{product.name}</h3>

        <p className="price">
          Rs. {product.price}
        </p>

        <p>
          <strong>Color:</strong> {product.color}
        </p>

        <p>
          <strong>Brand:</strong> {product.brand}
        </p>

        <p>
          <strong>Audience:</strong> {product.target_audience}
        </p>

        <a
          href={product.url}
          target="_blank"
          rel="noreferrer"
          className="view-btn"
        >
          View Product
        </a>

        <Link
          to={`/product/${product.id}`}
          className="view-btn"
        >
          View Details
        </Link>

        <button
          className="wishlist-btn"
          onClick={addToWishlist}
        >
          ❤️ Wishlist
        </button>

      </div>

    </div>

  );

}

export default ProductCard;