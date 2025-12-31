import axios from 'axios';
import Cookies from 'js-cookie';
export const getUserProfile = async () => {
  try {
    const response = await axios.post(
      `${process.env.REACT_APP_API}api/getProfile`,
      { email: Cookies.get('user_email') },
      {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      }
    );

    if (response.status === 200) {
      return response.data; // ✅ this will now be returned properly
    } else {
      return null;
    }
  } catch (error) {
    console.error("Error fetching user profile:", error);
    return null;
  }
};


export const saveUserProfile = async (name, email, avatar) => {
  try {
    const response = await axios.post(
      `${process.env.REACT_APP_API}api/saveProfile`,
      { name:name,email:Cookies.get('user_email') ,email1: email, avatar },
      {
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
        },
      }
    );

    if (response.status === 200) {
        Cookies.remove('token');
        Cookies.remove('user_email');
        window.location.href = '/login';
    } else {
      return false;
    }
  } catch (error) {
    console.error("Error saving user profile:", error);
    return false;
  }
};

export const ChangePassword= async (password, newPassword) => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API}api/changePassword`,
        { password, newPassword },
        {
          headers: {
            Authorization: `Bearer ${Cookies.get('token')}`,
          },
        });
        if (response.status === 200) {
            Cookies.remove('token');
            Cookies.remove('user_email');
            window.location.href = '/login';
        }
        else {
            return false;
        }
    }
    catch (error) {
        console.error("Error changing password:", error);
        return false;
    }
}