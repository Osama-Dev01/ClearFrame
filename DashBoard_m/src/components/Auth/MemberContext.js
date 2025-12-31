// // MemberContext.js
// import React, { createContext, useContext, useState } from 'react';

// const MemberContext = createContext();

// export const MemberProvider = ({ children }) => {
//   const [member, setMember] = useState(null);

//   const loginMember = (memberData) => {
//     setMember(memberData);
//   };

//   const logoutMember = () => {
//     setMember(null);
//     localStorage.removeItem('member_token');
//   };

//   return (
//     <MemberContext.Provider value={{ member, loginMember, logoutMember }}>
//       {children}
//     </MemberContext.Provider>
//   );
// };

// export const useMember = () => {
//   const context = useContext(MemberContext);
//   if (!context) {
//     throw new Error('useMember must be used within a MemberProvider');
//   }
//   return context;
// };


import React, { createContext, useContext, useState, useEffect } from 'react';

// 1. Create the context
const MemberContext = createContext(null);

// 2. Create the Provider component
export const MemberProvider = ({ children }) => {
  // --- STATE ---
  // Initialize state by reading from localStorage. This is the key to persistence.
  const [member, setMember] = useState(() => {
    try {
      const storedMember = localStorage.getItem('member_data');
      return storedMember ? JSON.parse(storedMember) : null;
    } catch (error) {
      return null;
    }
  });
  
  const [token, setToken] = useState(() => localStorage.getItem('member_token'));

  // --- LOGIN & LOGOUT FUNCTIONS ---
  
  /**
   * Updates the global state upon a successful login.
   * @param {object} memberData - The user object from the API (e.g., {id, username, email})
   * @param {string} memberToken - The JWT token from the API.
   */
  const loginMember = (memberData, memberToken) => {
    // Store in localStorage for persistence across page reloads
    localStorage.setItem('member_token', memberToken);
    localStorage.setItem('member_data', JSON.stringify(memberData));

    // Update the React state to trigger a re-render in all consuming components
    setToken(memberToken);
    setMember(memberData);
  };

  /**
   * Clears the authentication state globally.
   */
  const logoutMember = () => {
    // Clear from localStorage
    localStorage.removeItem('member_token');
    localStorage.removeItem('member_data');

    // Clear the React state
    setToken(null);
    setMember(null);
  };

  // --- VALUE TO BE PROVIDED TO CONSUMERS ---
  // We package up the state and functions to be shared.
  const value = {
    member,
    token, // <-- Now the token is provided
    loginMember,
    logoutMember,
    isMemberAuthenticated: !!token, // <-- A reliable boolean check
  };

  return (
    <MemberContext.Provider value={value}>
      {children}
    </MemberContext.Provider>
  );
};

// 3. Create the custom hook for easy consumption
export const useMember = () => {
  const context = useContext(MemberContext);
  if (!context) {
    throw new Error('useMember must be used within a MemberProvider');
  }
  return context;
};