// import React, { useState } from 'react';
// import Navbar from './components/Nav/Navbar';
// import Memsidebar from './components/Nav/Memsidebar';
// import Mnavbar from './components/Nav/Mnavbar'
// import Msidebar from './components/Nav/Msidebar'

// import Sidebar from './components/Nav/Sidebar';
// import { useMember } from './components/Auth/MemberContext'; // ⬅️ Import member context
// import { Routes, Route, useLocation } from 'react-router-dom';

// import Dashboard from './components/Dashboard/Dashboard';
// import MemberDashboard from './components/member_dash/member_dash';
// import Memposts from './components/Memposts/Memposts';

// import Login from './components/Auth/Login';
// import MemberLogin from './components/Auth/m_login';
// import Register from './components/Auth/Register';
// import Request from './components/request/request';
// import ExpenseList from './components/Expense/ExpenseList';
// import AccountManagement from './components/Accounts/Accounts';



// import NotFound from './components/NotFound/NotFound';
// import { TiThMenu } from "react-icons/ti";
// import { IoClose } from "react-icons/io5";

// import './App.css';

// function RoutesApp() {
//   const [menu, setMenu] = useState(false);
//   const location = useLocation();
//   const { member } = useMember(); // 👈 Get member data
//   const hideLayout = location.pathname === '/login' || location.pathname === '/register' || location.pathname === '/m_login';

//   return (
//     <div className="app">
//       {/* Conditional Navbar */}
//       {!hideLayout && (member ? <Navbar /> : <Navbar />)}

//       {/* Menu Toggle */}
//       {!hideLayout && !member && ( // 👈 only show toggle for admin layout
//         <div id='menuButt'>
//           {!menu ? (
//             <TiThMenu style={{ color: 'black', fontSize: 40 }} onClick={() => setMenu(!menu)} />
//           ) : (
//             <IoClose style={{ color: 'black', fontSize: 40 }} onClick={() => setMenu(!menu)} />
//           )}
//         </div>
//       )}

//       <div className="content-container">
//   {!hideLayout && (
//     member ? <Memsidebar menu={menu} /> : <Sidebar menu={menu} />
//   )}

//         <main className="main-content">
//           <Routes>
//             {/* Admin Routes */}
//             <Route path="/" element={<Dashboard />} />
//             <Route path="/request" element={<Request />} />
//             <Route path="/expenses" element={<ExpenseList />} />
           
//             <Route path="/account" element={<AccountManagement />} />

         
         

//             {/* Auth */}
//             <Route path="/login" element={<Login />} />
//             <Route path="/register" element={<Register />} />
//             <Route path="/m_login" element={<MemberLogin />} />

//             {/* Member Area */}
//             <Route path="/member" element={<MemberDashboard />} />
//             <Route path='/member/posts' element={<Memposts/>}/>

//             {/* Fallback */}
//             <Route path="*" element={<NotFound />} />
//           </Routes>
//         </main>
//       </div>
//     </div>
//   );
// }

// export default RoutesApp;



import React, { useState } from 'react';
// ❌ Navbar and Mnavbar imports removed
import Memsidebar from './components/Nav/Memsidebar';
import Sidebar from './components/Nav/Sidebar'; // Assuming 'Sidebar' is the admin sidebar

import { useMember } from './components/Auth/MemberContext';
import { Routes, Route, useLocation } from 'react-router-dom';

// Import your components
import Dashboard from './components/Dashboard/Dashboard';
import Msidebar from './components/Nav/Msidebar';
import MemberDashboard from './components/member_dash/member_dash';
import Memposts from './components/Memposts/Memposts';
import MyActivity from './components/Memposts/Memactivity';
import Profile from './components/Memposts/profile';
import Login from './components/Auth/Login';
import MemberLogin from './components/Auth/m_login';
import Register from './components/Auth/Register';
import Request from './components/request/request';
import MemberList from './components/Expense/ExpenseList'; 
import MView from './components/Expense/Mveiw'; 
import AccountManagement from './components/Accounts/Accounts';
import NotFound from './components/NotFound/NotFound';

// Icons
import { TiThMenu } from "react-icons/ti";
import { IoClose } from "react-icons/io5";

import './App.css';

function RoutesApp() {
  const [menu, setMenu] = useState(false);
  const location = useLocation();
  const { member } = useMember(); // Get member data
  
  // This logic correctly hides the layout on auth pages
  const hideLayout = location.pathname === '/login' 
                  || location.pathname === '/register' 
                  || location.pathname === '/m_login';

  return (
    <div className="app">
      {/* ❌ The entire conditional Navbar block has been deleted. */}
      
      <div className="content-container">
        {/* --- Sidebar --- */}
        {/* This logic remains the same: show the correct sidebar if not on an auth page */}
        {!hideLayout && (
          member ? <Msidebar menu={menu} /> : <Sidebar menu={menu} />
        )}

        {/* --- Main Content Area --- */}
        <main className="main-content">
          {/* --- Menu Toggle Button (Now inside Main Content) --- */}
          {/* We keep the logic to only show this for the admin layout */}
          {!hideLayout && !member && (
            <div id='menuButt'>
              {!menu ? (
                <TiThMenu style={{ color: 'black', fontSize: 40 }} onClick={() => setMenu(!menu)} />
              ) : (
                <IoClose style={{ color: 'black', fontSize: 40 }} onClick={() => setMenu(!menu)} />
              )}
            </div>
          )}

          {/* --- Your Application Routes --- */}
          <Routes>
            {/* Admin Routes */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/request" element={<Request />} />
            <Route path="/expenses" element={<MemberList />} />
            <Route path="/account" element={<AccountManagement />} />

            {/* Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/m_login" element={<MemberLogin />} />
           

            {/* Member Area Routes */}
            <Route path="/member" element={<MemberDashboard />} />
            <Route path='/member/posts' element={<Memposts />} />
            <Route path='/member/activity' element={<MyActivity/>}/>
            <Route path='/member/profile' element={<Profile/>}/>
            

            {/* Fallback Route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default RoutesApp;
