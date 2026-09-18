import streamlit as st

from services.auth_service import create_users_table

from components.login import show_login
from components.register import show_register
from components.profile import show_profile

from services.description_service import generate_product_description


from recommendation.personalized_recommendation import (
    get_search_aware_recommendations
)

from database import (
    add_to_cart,
    get_cart_items,
    create_direct_order,
    remove_from_cart,
    clear_cart,
    create_cart_order,
    get_cart_total,
    get_user_orders,
    get_order_items,
    add_to_wishlist,
    get_wishlist,
    remove_from_wishlist,
    clear_wishlist,
    save_search_query,
    get_search_history,
    add_recently_viewed,
    get_recently_viewed
   
)


from recommendation.embedding_service import (
    get_embedding_recommendations
)

from services.notification_service import (
    send_order_email,
    send_whatsapp_message
)


from agent import graph




# =========================
# INITIAL SETUP
# =========================
create_users_table()

st.set_page_config(
    page_title="AI Shopping Assistant",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 AI Shopping Assistant")


# =========================
# SESSION STATE
# =========================

if "viewed_product" not in st.session_state:
    st.session_state.viewed_product = None

if "user" not in st.session_state:
    st.session_state.user = None

if "output" not in st.session_state:
    st.session_state.output = None

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

if "show_cart_checkout" not in st.session_state:
    st.session_state.show_cart_checkout = False



# =========================
# AUTHENTICATION
# =========================
if not st.session_state.user:

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "📝 Register"]
    )

    with login_tab:
        show_login()

    with register_tab:
        show_register()

    st.stop()


# =========================
# HEADER
# =========================
col1, col2 = st.columns([4, 1])

with col1:
    st.write(
        f"Welcome, **{st.session_state.user['full_name']}** 👋"
    )

with col2:
    if st.button("Logout"):

        st.session_state.user = None
        st.session_state.output = None
        st.session_state.selected_product = None

        st.rerun()

# =========================
# RECOMMENDATIONS SECTION
# =========================
if st.session_state.user:

    recommendations = get_search_aware_recommendations(
        st.session_state.user["id"]
    )

    if recommendations:

        st.divider()
        st.subheader("🤖 Recommended For You")

        cols = st.columns(min(len(recommendations), 4))

        for idx, item in enumerate(recommendations):

            with cols[idx % 4]:

                with st.container(border=True):

                    # =========================
                    # IMAGE
                    # =========================
                    try:
                        if item["image"]:
                            st.image(
                                item["image"],
                                use_container_width=True
                            )
                    except:
                        pass

                    # =========================
                    # BASIC INFO
                    # =========================
                    st.markdown(f"### {item['name']}")
                    st.write(f"💰 Rs. {item['price']}")

                    # =========================
                    # VIEW BUTTON
                    # =========================
                    if st.button(
                        "View",
                        key=f"view_{item['id']}"
                    ):

                        st.session_state.viewed_product = (
                            item["id"],
                            None,
                            item["name"],
                            item["price"],
                            item["color"],
                            item["brand"],
                            item["image"],
                            item["url"],
                            item["target_audience"],
                            item["category"]
                        )

                        st.rerun()


# =========================
# PRODUCT DETAILS PAGE
# =========================
if st.session_state.get("viewed_product"):

    product = st.session_state.viewed_product

    st.divider()
    st.subheader("👁 Product Details")

    col1, col2 = st.columns([1, 2])

    with col1:
        if product[6]:
            st.image(product[6], use_container_width=True)

    with col2:
        st.markdown(f"### {product[2]}")
        st.write(f"💰 Price: Rs. {product[3]}")
        st.write(f"🎨 Color: {product[4]}")
        st.write(f"🏷 Brand: {product[5]}")
        st.write(f"👤 Audience: {product[8]}")
        st.write(f"📦 Category: {product[9]}")

        if product[7]:
            st.link_button("🌐 Visit Product", product[7])

    # =========================
    # AI DESCRIPTION SECTION
    # =========================
    st.divider()
    st.subheader("🧠 AI Description")

    # optional caching
    try:
        with st.spinner("Generating AI description..."):
            desc = generate_product_description(product)
            st.success(desc)
    except Exception:
        st.error("AI description not available")

    # =========================
    # BACK BUTTON
    # =========================
    if st.button("⬅ Back to Recommendations"):
        st.session_state.viewed_product = None
        st.rerun()

# =========================
# TABS
# =========================
search_tab, cart_tab, orders_tab,wishlist_tab,history_tab,recent_tab, profile_tab = st.tabs(
    [
        "🔍 Search Products",
        "🛒 Cart",
        "📦 My Orders",
        "❤️ Wishlist",
        "🔍 Search History",
        "🕒 Recently Viewed",
        "👤 Profile"
    ]
)


# =========================
# SEARCH TAB
# =========================
with search_tab:

    question = st.text_input(
        "",
        placeholder="Show me black kameez shalwar in L size"
    )

    if st.button("Search") and question:

        with st.spinner("Searching..."):

            # Save search history (IMPORTANT)
            save_search_query(
                st.session_state.user["id"],
                question
            )

            st.session_state.output = graph.invoke(
                {"question": question}
            )

# =========================
# DISPLAY RESULTS
# =========================
if st.session_state.output:

    output = st.session_state.output

    st.subheader("Detected Route")
    st.write(output["route"])

    with st.expander("Generated SQL"):
        st.code(output["sql"], language="sql")

    results = output["result"]

    if not results:

        st.warning("No products found")

    elif isinstance(results[0], str):

        st.error(results[0])

    else:

        st.success(f"Found {len(results)} products")

        cols = st.columns(3)

        for idx, row in enumerate(results):

            with cols[idx % 3]:

                with st.container(border=True):

                    # =========================
                    # IMAGE
                    # =========================
                    try:
                        if row[6]:
                            st.image(
                                row[6],
                                use_container_width=True
                            )
                    except Exception:
                        pass

                    # =========================
                    # PRODUCT INFO
                    # =========================
                    st.markdown(f"### {row[2]}")
                    st.markdown(f"💰 Rs. {row[3]}")
                    st.markdown(f"🎨 {row[4]}")
                    st.markdown(f"🏷 {row[5]}")
                    st.markdown(f"👤 {row[8]}")

                    user_id = st.session_state.user["id"]

                    # =========================
                    # VIEW PRODUCT
                    # =========================
                    if row[7]:

                        st.link_button(
                            "View Product",
                            row[7],
                            use_container_width=True,
                            key=f"view_{row[0]}"
                        )

                    # =========================
                    # BUY NOW
                    # =========================
                    if st.button(
                        "🛒 Buy Now",
                        key=f"buy_{row[0]}"
                    ):

                        add_recently_viewed(user_id, row[0])

                        st.session_state.selected_product = row
                        st.rerun()

                    # =========================
                    # ADD TO CART
                    # =========================
                    if st.button(
                        "➕ Add to Cart",
                        key=f"cart_{row[0]}"
                    ):

                        add_to_cart(
                            user_id=user_id,
                            product_id=row[0]
                        )

                        add_recently_viewed(user_id, row[0])

                        st.success("Added to cart 🛒")
                        st.rerun()

                    # =========================
                    # ADD TO WISHLIST
                    # =========================
                    if st.button(
                        "❤️ Wishlist",
                        key=f"wish_{row[0]}"
                    ):

                        add_to_wishlist(
                            user_id=user_id,
                            product_id=row[0]
                        )

                        add_recently_viewed(user_id, row[0])

                        st.success("Added to wishlist ❤️")
                        st.rerun()

                    if st.button(
                        "👁 View Details",
                        key=f"details_{row[0]}"
                    ):                  
                    
                        add_recently_viewed(
                            st.session_state.user["id"],
                            row[0]
                        )
                        st.session_state.viewed_product = row
                        st.write("VIEW BUTTON CLICKED")  # Debug
                        st.rerun()

# =========================
# PRODUCT DETAILS
# =========================

if st.session_state.get("viewed_product"):

    product = st.session_state.viewed_product

    st.divider()

    st.subheader("👁 Product Details")

    col1, col2 = st.columns([1, 2])

    with col1:

        try:
            if product[6]:
                st.image(
                    product[6],
                    use_container_width=True
                )
        except:
            pass

    with col2:

        st.markdown(f"### {product[2]}")
        st.write(f"💰 Price: Rs. {product[3]}")
        st.write(f"🎨 Color: {product[4]}")
        st.write(f"🏷 Brand: {product[5]}")
        st.write(f"👤 Audience: {product[8]}")

        with st.expander("🧠 AI Description"):
            try:
                desc = generate_product_description(row)
                st.write(desc)
            except Exception as e:
                st.write("Description unavailable")

        if product[7]:
            st.link_button(
                "🌐 Visit Website",
                product[7]
            )

        if st.button(
            "🛒 Buy This Product",
            key=f"detail_buy_{product[0]}"
        ):

            st.session_state.selected_product = product
            st.rerun()



# =========================
# CHECKOUT SECTION
# =========================
if st.session_state.selected_product:

    product = st.session_state.selected_product

    recommendations = get_embedding_recommendations(
        product_id=product[0]
    )

    st.divider()

    st.subheader("💳 Checkout")

    st.write(f"**Product:** {product[2]}")
    st.write(f"**Price:** Rs. {product[3]}")

    with st.form("checkout_form"):

        customer_name = st.text_input(
            "Full Name",
            value=st.session_state.user["full_name"]
        )

        customer_email = st.text_input(
            "Email",
            value=st.session_state.user["email"]
        )

        phone = st.text_input("Phone Number")

        address = st.text_area("Delivery Address")

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1
        )

        st.markdown("### Payment (Simulation Only)")

        card_number = st.text_input(
            "Card Number",
            type="password"
        )

        expiry = st.text_input("Expiry Date")

        cvv = st.text_input(
            "CVV",
            type="password"
        )

        submit_order = st.form_submit_button(
            "Place Order"
        )

        if submit_order:

            if not customer_name or not phone or not address:
            
                st.error("Please fill all required fields.")

            else:
            
                order_id = create_direct_order(
                    user_id=st.session_state.user["id"],
                    product_id=product[0],
                    product_name=product[2],
                    price=product[3],
                    customer_name=customer_name,
                    phone=phone,
                    address=address,
                    quantity=quantity
                )

                send_order_email(
                    customer_email=customer_email,
                    customer_name=customer_name,
                    product_name=product[2],
                    quantity=quantity
                )

                send_whatsapp_message(
                    phone=phone,
                    product_name=product[2]
                )

                st.success("✅ Order placed successfully!")
                st.balloons()

                st.success(f"Order ID #{order_id} created")

                st.session_state.selected_product = None
                st.rerun()

    # =========================
    # AI RECOMMENDATIONS
    # =========================
    if recommendations:

        st.divider()

        st.subheader("🤖 AI Recommendations")

        cols = st.columns(
            min(len(recommendations), 4)
        )

        for idx, item in enumerate(recommendations):

            with cols[idx]:

                with st.container(border=True):

                    try:
                        if item["image"]:
                            st.image(
                                item["image"],
                                use_container_width=True
                            )
                    except Exception:
                        pass

                    st.markdown(f"### {item['name']}")
                    st.markdown(f"💰 Rs. {item['price']}")
                    st.markdown(f"🎨 {item['color']}")
                    st.markdown(f"🏷 {item['brand']}")
                    st.markdown(f"👤 {item['target_audience']}")

                    if item["url"]:
                        st.link_button(
                            "View Product",
                            item["url"],
                            key=f"emb_link_{item['id']}",
                            use_container_width=True
                        )

                    if st.button(
                        "🛒 Buy This",
                        key=f"emb_buy_{item['id']}"
                    ):

                        st.session_state.selected_product = (
                            item["id"],
                            item["product_id"],
                            item["name"],
                            item["price"],
                            item["color"],
                            item["brand"],
                            item["image"],
                            item["url"],
                            item["target_audience"],
                            item["category"]
                        )

                        st.rerun()


# =========================
# ORDERS TAB
# =========================
with orders_tab:

    st.subheader("📦 My Orders")

    orders = get_user_orders(
    st.session_state.user["id"]
    )

    if not orders:

        st.info("No orders placed yet.")

    else:

        for order in orders:

            order_id = order[0]
            total_amount = order[1]
            created_at = order[2]

            with st.container(border=True):
            
                st.markdown(f"### Order #{order_id}")

                st.write(f"💰 Total: Rs. {total_amount}")
                st.write(f"🕒 Ordered: {created_at}")

                items = get_order_items(order_id)

                st.write("### Items")

                for item in items:
                
                    st.write(
                        f"• {item[0]} × {item[1]} "
                        f"(Rs. {item[2]})"
                    )


# =========================
# CART TAB
# =========================

if "show_cart_checkout" not in st.session_state:
    st.session_state.show_cart_checkout = False

with cart_tab:

    st.subheader("🛒 My Cart")

    cart_items = get_cart_items(
        st.session_state.user["id"]
    )

    if not cart_items:

        st.info("Your cart is empty.")

        st.session_state.show_cart_checkout = False

    else:

        total = 0

        for item in cart_items:

            cart_id = item[0]
            product_id = item[1]
            name = item[2]
            price = item[3]
            image = item[4]
            color = item[5]
            brand = item[6]
            quantity = item[7]

            subtotal = price * quantity
            total += subtotal

            with st.container(border=True):

                col1, col2 = st.columns([1, 3])

                with col1:

                    if image:
                        st.image(
                            image,
                            use_container_width=True
                        )

                with col2:

                    st.markdown(f"### {name}")
                    st.write(f"🎨 {color}")
                    st.write(f"🏷 {brand}")
                    st.write(f"📦 Quantity: {quantity}")
                    st.write(f"💰 Rs. {subtotal}")

                    if st.button(
                        "❌ Remove",
                        key=f"remove_{cart_id}"
                    ):

                        remove_from_cart(cart_id)

                        st.rerun()

        st.divider()

        st.subheader(f"Total: Rs. {total}")

        col1, col2 = st.columns([3, 1])

        with col1:

            if st.button(
                "🛍 Checkout Cart",
                key="open_cart_checkout"
            ):

                st.session_state.show_cart_checkout = True

                st.rerun()

        with col2:

            if st.button(
                "🗑 Clear Cart",
                key="clear_cart"
            ):

                clear_cart(
                    st.session_state.user["id"]
                )

                st.session_state.show_cart_checkout = False

                st.rerun()

        # =========================
        # CHECKOUT FORM
        # =========================

        if st.session_state.show_cart_checkout:

            st.divider()

            st.subheader("💳 Cart Checkout")

            with st.form("cart_checkout_form"):

                customer_name = st.text_input(
                    "Full Name",
                    value=st.session_state.user["full_name"]
                )

                customer_email = st.text_input(
                    "Email",
                    value=st.session_state.user["email"]
                )

                phone = st.text_input(
                    "Phone Number"
                )

                address = st.text_area(
                    "Delivery Address"
                )

                st.markdown(
                    "### Payment (Simulation Only)"
                )

                card_number = st.text_input(
                    "Card Number",
                    type="password"
                )

                expiry = st.text_input(
                    "Expiry Date (MM/YY)"
                )

                cvv = st.text_input(
                    "CVV",
                    type="password"
                )

                submit_cart = st.form_submit_button(
                    "✅ Place Order"
                )

                if submit_cart:

                    if not phone or not address:

                        st.error(
                            "Please fill all required fields."
                        )

                    else:

                        order_id = create_cart_order(
                            user_id=st.session_state.user["id"],
                            customer_name=customer_name,
                            phone=phone,
                            address=address
                        )

                        if order_id:

                            send_order_email(
                                customer_email=customer_email,
                                customer_name=customer_name,
                                product_name="Multiple Products",
                                quantity=len(cart_items)
                            )

                            send_whatsapp_message(
                                phone=phone,
                                product_name="Multiple Products"
                            )

                            st.success(
                                f"✅ Order #{order_id} placed successfully!"
                            )

                            st.balloons()

                            st.session_state.show_cart_checkout = False

                            st.rerun()

                        else:

                            st.error(
                                "Failed to place order."
                            )


# =========================
# WISHLIST UI
# =========================

with wishlist_tab:

    st.subheader("❤️ My Wishlist")

    # =========================
    # CLEAR WISHLIST BUTTON
    # =========================
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🗑 Clear Wishlist"):

            clear_wishlist(st.session_state.user["id"])
            st.success("Wishlist cleared ❤️")
            st.rerun()

    st.divider()

    # =========================
    # LOAD ITEMS
    # =========================
    items = get_wishlist(st.session_state.user["id"])

    if not items:
        st.info("Wishlist is empty")

    else:

        cols = st.columns(3)

        for idx, row in enumerate(items):

            with cols[idx % 3]:

                with st.container(border=True):

                    if row[6]:
                        st.image(row[6], use_container_width=True)

                    st.markdown(f"### {row[2]}")
                    st.markdown(f"💰 Rs. {row[3]}")
                    st.markdown(f"🎨 {row[4]}")
                    st.markdown(f"🏷 {row[5]}")

                    if row[7]:
                        st.link_button(
                            "View Product",
                            row[7],
                            key=f"wish_link_{row[0]}"
                        )

                    # =========================
                    # REMOVE SINGLE ITEM
                    # =========================
                    if st.button(
                        "❌ Remove",
                        key=f"rm_wish_{row[0]}"
                    ):

                        remove_from_wishlist(
                            st.session_state.user["id"],
                            row[0]
                        )

                        st.rerun()

                    # =========================
                    # BUY NOW FROM WISHLIST
                    # =========================
                    if st.button(
                        "🛒 Buy Now",
                        key=f"wish_buy_{row[0]}"
                    ):

                        st.session_state.selected_product = row
                        st.rerun()


# =========================
# SEARCH HISTORY TAB
# =========================

with history_tab:

    st.subheader("🕘 Your Search History")

    from database import get_search_history

    history = get_search_history(st.session_state.user["id"])

    if not history:
        st.info("No search history yet.")

    else:

        for item in history:

            query, created_at = item

            st.markdown(
                f"🔎 **{query}**  \n"
                f"🕒 {created_at}"
            )

            st.divider()


# =========================
# RECENTLY VIEWED
# =========================

with recent_tab:

    st.subheader("🕒 Recently Viewed Products")

    items = get_recently_viewed(st.session_state.user["id"])

    if not items:
        st.info("No recently viewed products yet.")

    else:
        cols = st.columns(3)

        for idx, row in enumerate(items):

            with cols[idx % 3]:

                with st.container(border=True):

                    if row[6]:
                        st.image(row[6], use_container_width=True)

                    st.markdown(f"### {row[2]}")
                    st.markdown(f"💰 Rs. {row[3]}")
                    st.markdown(f"🎨 {row[4]}")
                    st.markdown(f"🏷 {row[5]}")

                    if row[7]:
                        st.link_button("View Product", row[7])

                    if st.button("🛒 Buy Again", key=f"recent_buy_{row[0]}"):
                        st.session_state.selected_product = row
                        st.rerun()

# =========================
# PROFILE TAB
# =========================
with profile_tab:
    show_profile()