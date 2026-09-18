import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function Wishlist() {
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user"));

  const [items, setItems] = useState([]);

  // Load Wishlist
  const loadWishlist = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/wishlist/${user.id}`
      );
      setItems(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    loadWishlist();
  }, []);

  // Remove Item
  const removeItem = async (wishlistId) => {
    try {
      await axios.delete(
        `http://localhost:8000/wishlist/${wishlistId}`
      );
      loadWishlist();
    } catch (error) {
      console.log(error);
    }
  };

  // Clear Wishlist
  const clearWishlist = async () => {
    try {
      await axios.delete(
        `http://localhost:8000/wishlist/clear/${user.id}`
      );
      loadWishlist();
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="wishlist-container">

      {/* HEADER */}
      <div className="wishlist-header">
        <div>
          <h1 className="wishlist-title">Your Wishlist</h1>
          <p className="item-count">{items.length} Items Saved</p>
        </div>

        {items.length > 0 && (
          <button className="clear-btn" onClick={clearWishlist}>
            🗑 Clear Wishlist
          </button>
        )}
      </div>

      {/* GRID */}
      {items.length === 0 ? (
        <h3>No items in wishlist</h3>
      ) : (
        <div className="wishlist-grid">

          {items.map((item) => (
            <div className="wishlist-card" key={item.wishlist_id}>

              {/* REMOVE BTN */}
              <button
                className="remove-btn"
                onClick={() => removeItem(item.wishlist_id)}
              >
                ✕
              </button>

              {/* IMAGE */}
              <div className="card-img-wrap">
                <img src={item.image} alt={item.name} />
              </div>

              {/* INFO */}
              <div className="card-details">

                <h3 className="card-title">
                  {item.name}
                </h3>

                <p className="card-price">
                  Rs. {item.price}
                </p>

                <p className="muted">
                  {item.brand} • {item.color}
                </p>

              </div>

              {/* ACTIONS */}
              <button
                className="btn-add-cart"
                onClick={() =>
                  navigate(`/product/${item.product_id}`)
                }
              >
                View Details
              </button>

            </div>
          ))}

        </div>
      )}

    </div>
  );
}

export default Wishlist;