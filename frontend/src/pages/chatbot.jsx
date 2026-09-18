import { useState } from "react";
import axios from "axios";
import "./Chatbot.css";

const user = JSON.parse(
    localStorage.getItem("user")
);


function Chatbot() {

    const [messages, setMessages] = useState([]);

    const [input, setInput] = useState("");

    const [loading, setLoading] = useState(false);



    const sendMessage = async () => {

        if (!input.trim()) return;


        const userMessage = {
            role: "user",
            content: input
        };


        setMessages(prev => [
            ...prev,
            userMessage
        ]);


        setInput("");

        setLoading(true);


        try {


            const response = await axios.post(
               "http://localhost:8000/chat",
                {
                    user_id: user?.id || 1,
                    message: userMessage.content
                }
            );


            const botMessage = {

                role: "assistant",

                content: response.data.answer

            };


            setMessages(prev => [
                ...prev,
                botMessage
            ]);



        } catch(error) {


            console.log(error);


            setMessages(prev => [

                ...prev,

                {
                    role:"assistant",
                    content:"Sorry, something went wrong."
                }

            ]);

        }


        setLoading(false);

    };



    const handleKeyPress = (e)=>{

        if(e.key==="Enter")
        {
            sendMessage();
        }

    };



    return (

        <div className="chatbot-page">


            <div className="chatbot-container">


                <div className="chatbot-header">

                    🤖 AI Shopping Assistant

                </div>



                <div className="chat-messages">


                    {
                        messages.map((msg,index)=>(


                            <div

                                key={index}

                                className={
                                    msg.role==="user"
                                    ?
                                    "message user-message"
                                    :
                                    "message bot-message"
                                }

                            >

                                {msg.content}


                            </div>


                        ))
                    }


                    {
                        loading && (

                            <div className="message bot-message">

                                Thinking...

                            </div>

                        )
                    }


                </div>





                <div className="chat-input-area">


                    <input

                        type="text"

                        placeholder="Ask about policies, products, delivery..."

                        value={input}

                        onChange={(e)=>
                            setInput(e.target.value)
                        }

                        onKeyDown={handleKeyPress}

                    />



                    <button

                        onClick={sendMessage}

                    >

                        Send

                    </button>


                </div>



            </div>


        </div>

    );


}


export default Chatbot;