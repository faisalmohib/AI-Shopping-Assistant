import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import ProductDetails
from "./pages/ProductDetails";
import Cart from "./pages/Cart";
import Profile from "./pages/Profile";
import Checkout from "./pages/Checkout";
import Orders from "./pages/Orders";
import OrderDetails from "./pages/OrderDetails";
import Wishlist from "./pages/Wishlist";
import RecentlyViewed from "./pages/RecentlyViewed";
import SearchHistory from "./pages/SearchHistory";
import Chatbot from "./pages/Chatbot";
import ChatbotButton from "./components/ChatbotButton";

import Navbar from "./components/Navbar";

import "./App.css";

function App() {
  return (
    <BrowserRouter>

      <Navbar />

      <Routes>

        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route
          path="/profile"
          element={<Profile />}
        />

        <Route
          path="/product/:id"
            element={<ProductDetails />}
        />

        <Route 
         path="/chatbot"
         element={<Chatbot />}
        />

        <Route
          path="/cart"
          element={<Cart />}
        />
      

        <Route
          path="/checkout"
          element={<Checkout />}
        />
          
        <Route
          path="/checkout/:id"
          element={<Checkout />}
        />

        <Route
          path="/orders"
          element={<Orders />}
        />

        <Route
          path="/wishlist"
          element={<Wishlist />}
        />
        <Route
            path="/recently-viewed"
            element={<RecentlyViewed />}
        />
          
        <Route
            path="/search-history"
            element={<SearchHistory />}
        />

        <Route
          path="/order/:id"
          element={<OrderDetails />}
        />

      </Routes>

      <ChatbotButton/>

    </BrowserRouter>
  );
}

export default App;