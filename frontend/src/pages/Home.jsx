import { useState, useEffect } from "react";
import axios from "axios";
import ProductCard from "../components/ProductCard";
import { useNavigate } from "react-router-dom";

function Home() {

  const navigate = useNavigate();

  const [question, setQuestion] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const [recommendations, setRecommendations] = useState([]);

  const user = JSON.parse(
    localStorage.getItem("user")
  );

  // ----------------------------
  // SEARCH PRODUCTS
  // ----------------------------
  const searchProducts = async () => {

    if (!question.trim()) return;

    try {

      setLoading(true);

      const response = await axios.post(
        "http://localhost:8000/search",
        {
          question: question
        }
      );

      setProducts(response.data.products || []);

      // Save search history
      if (user) {

        await axios.post(
          "http://localhost:8000/search/history",
          {
            user_id: user.id,
            query: question
          }
        );

        // refresh recommendations after search
        loadRecommendations();

      }

    } catch (error) {

      console.error(error);
      alert("Search Failed");

    } finally {

      setLoading(false);

    }

  };

  // ----------------------------
  // LOAD RECOMMENDATIONS
  // ----------------------------
  const loadRecommendations = async () => {

    try {

      if (!user) return;

      const response = await axios.get(
        `http://localhost:8000/recommendations/${user.id}`
      );

      setRecommendations(response.data || []);

    } catch (error) {

      console.log(error);

    }

  };

  // ----------------------------
  // INIT LOAD
  // ----------------------------
  useEffect(() => {

    loadRecommendations();

  }, []);

  return (
  <>

    {/* Hero Section */}

    <header className="ai-hero-section">

      <div className="container">

        <h1 className="ai-title">
          AI Shopping <span>Assistant</span>
        </h1>

        <p className="ai-subtitle">
          Find exactly what you are looking for. Ask me anything or explore smart products.
        </p>

        <div className="search-container">

          <input
            type="text"
            className="search-input"
            placeholder="e.g. Show me black kameez shalwar in L size..."
            value={question}
            onChange={(e) =>
              setQuestion(e.target.value)
            }
          />

          <button
            className="btn-search"
            onClick={searchProducts}
          >
            Search
          </button>

        </div>

      </div>

    </header>

    {/* Main Content */}

    <main className="container">

      {loading && (
        <h2
          style={{
            textAlign: "center",
            marginBottom: "30px"
          }}
        >
          Searching...
        </h2>
      )}

      {/* Search Results */}

      {products.length > 0 && (
        <>

          <h2 className="section-title">
            Search Results
          </h2>

          <div className="products-grid">

            {products.map((product) => (

              <div
                key={product.id}
                className="product-card-link"
              >

                <div className="product-card">

                  <div className="card-img-wrap">

                    <img
                      src={product.image}
                      alt={product.name}
                    />

                  </div>

                  <div className="card-meta-row">

                    <span className="brand-name">
                      {product.brand}
                    </span>

                    <span className="color-info">
                      {product.color}
                    </span>

                  </div>

                  <h3 className="card-title">
                    {product.name}
                  </h3>

                  <p className="card-price">
                    Rs. {product.price}
                  </p>

                  <button
                    className="btn-view-details"
                    onClick={() =>
                      navigate(`/product/${product.id}`)
                    }
                  >
                    View Details
                  </button>

                </div>

              </div>

            ))}

          </div>

        </>
      )}

      {/* Recommendations */}

      {recommendations.length > 0 && (

        <>

          <h2 className="section-title">
            Recommended For You
          </h2>

          <div className="products-grid">

            {recommendations.map((product) => (

              <div
                key={product.id}
                className="product-card-link"
              >

                <div className="product-card">

                  <div className="card-img-wrap">

                    <img
                      src={product.image}
                      alt={product.name}
                    />

                  </div>

                  <div className="card-meta-row">

                    <span className="brand-name">
                      {product.brand}
                    </span>

                    <span className="color-info">
                      {product.color}
                    </span>

                  </div>

                  <h3 className="card-title">
                    {product.name}
                  </h3>

                  <p className="card-price">
                    Rs. {product.price}
                  </p>

                  <button
                    className="btn-view-details"
                    onClick={() =>
                      navigate(`/product/${product.id}`)
                    }
                  >
                    View Details
                  </button>

                </div>

              </div>

            ))}

          </div>

        </>

      )}

    </main>

  </>
);

}

export default Home;