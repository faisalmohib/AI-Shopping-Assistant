function Profile() {
  const user = JSON.parse(
    localStorage.getItem("user")
  );

  if (!user) {
    return <h2>Please Login</h2>;
  }

  return (
    <div className="profile-container">

      <div className="profile-card">

        <div className="avatar">
          {user.full_name[0].toUpperCase()}
        </div>

        <h2>{user.full_name}</h2>

        <p>{user.email}</p>

      </div>

    </div>
  );
}

export default Profile;