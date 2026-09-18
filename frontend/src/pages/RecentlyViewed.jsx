import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function RecentlyViewed() {
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user"));

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);

      const response = await axios.get(
        `http://localhost:8000/recently-viewed/${user.id}`
      );

      setProducts(response.data);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="recent-container">

      {/* HEADER */}
      <div className="recent-header">
        <h1 className="recent-title">Recently Viewed</h1>
        <p className="recent-subtitle">
          Products you explored recently
        </p>
      </div>

      {/* LOADING */}
      {loading && <p>Loading...</p>}

      {/* EMPTY STATE */}
      {!loading && products.length === 0 && (
        <div className="empty-state">
          <h3>No recently viewed products</h3>
          <p>Start exploring products to see them here</p>
        </div>
      )}

      {/* GRID */}
      <div className="recent-grid">

        {products.map((product) => (
          <div
            key={product.id}
            className="recent-card"
            onClick={() => navigate(`/product/${product.id}`)}
          >

            <div className="recent-img-wrap">
              <img src={product.image} alt={product.name} />
            </div>

            <div className="recent-info">

              <h3 className="recent-name">
                {product.name}
              </h3>

              <p className="recent-price">
                Rs. {product.price}
              </p>

              <p className="recent-meta">
                {product.brand} • {product.color}
              </p>

            </div>

          </div>
        ))}

      </div>

    </div>
  );
}

export default RecentlyViewed;