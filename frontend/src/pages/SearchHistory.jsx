import { useEffect, useState } from "react";
import axios from "axios";

function SearchHistory() {
  const user = JSON.parse(localStorage.getItem("user"));

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);

      const response = await axios.get(
        `http://localhost:8000/search/history/${user.id}`
      );

      setHistory(response.data);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="history-container">

      {/* HEADER */}
      <div className="history-header">
        <h1 className="history-title">Search History</h1>
        <p className="history-subtitle">
          Your recent product searches
        </p>
      </div>

      {/* LOADING */}
      {loading && <p>Loading...</p>}

      {/* EMPTY STATE */}
      {!loading && history.length === 0 && (
        <div className="empty-state">
          <h3>No search history yet</h3>
          <p>Start searching products to see history here</p>
        </div>
      )}

      {/* HISTORY LIST */}
      <div className="history-grid">

        {history.map((item, index) => (
          <div key={index} className="history-card">

            <div className="history-query">
              🔍 {item.query}
            </div>

            <div className="history-meta">
              <span className="history-date">
                {new Date(item.created_at).toLocaleString()}
              </span>
            </div>

          </div>
        ))}

      </div>

    </div>
  );
}

export default SearchHistory;