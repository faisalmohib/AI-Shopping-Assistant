import { useNavigate } from "react-router-dom";
import "./ChatbotButton.css";


function ChatbotButton() {

    const navigate = useNavigate();


    return (

        <button
            className="chatbot-floating-btn"
            onClick={() => navigate("/chatbot")}
        >

            🤖

        </button>

    );

}


export default ChatbotButton;