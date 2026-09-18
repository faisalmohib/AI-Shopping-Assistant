import { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] =
    useState("");

  const loginUser = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        "http://localhost:8000/login",
        {
          email,
          password,
        }
      );

      if (response.data.success) {
        localStorage.setItem(
          "user",
          JSON.stringify(response.data.user)
        );

        alert("Login Successful");

        navigate("/");
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      console.error(error);
      alert("Login Failed");
    }
  };

  return (
    <div className="auth-container">

      <form
        className="auth-form"
        onSubmit={loginUser}
      >
        <h2>Login</h2>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        <button type="submit">
          Login
        </button>

        <p>
          Don't have an account?{" "}
          <Link to="/register">
            Register
          </Link>
        </p>

      </form>

    </div>
  );
}

export default Login;