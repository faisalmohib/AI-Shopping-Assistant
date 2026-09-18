import { Link, useNavigate } from "react-router-dom";


function Navbar() {
  const navigate = useNavigate();

  const user = JSON.parse(
    localStorage.getItem("user")
  );

  const logout = () => {
    localStorage.removeItem("user");

    navigate("/login");

    window.location.reload();
  };

  return (
    <nav className="navbar">

      <Link
        to="/"
        className="logo"
      >
        AI_Shop
      </Link>

      <div className="nav-links">

        {!user ? (
          <>
            <Link to="/login">
              Login
            </Link>

            <Link to="/register">
              Register
            </Link>
          </>
        ) : (
          <>
            
            <Link to="/cart">
                Cart
            </Link>
            <Link to="/profile">
              {user.full_name}
            </Link>

            <Link to="/wishlist">
              ❤️ Wishlist
            </Link>

            <Link to="/recently-viewed">
                Recently Viewed
            </Link>
                    
            <Link to="/search-history">
                Search History
            </Link>
            <Link to="/orders">
            
             <button>
                My Orders
              </button>
            </Link>

            <button
              className="logout-btn"
              onClick={logout}
            >
              Logout
            </button>
          </>
        )}

      </div>

    </nav>
  );
}

export default Navbar;