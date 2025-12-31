import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell
} from 'recharts';
import {
  FiUsers,
  FiUserCheck,
  FiFileText,
  FiShield,
  FiUserPlus
} from 'react-icons/fi';
import './Dashboard.css';
const COLORS = ['#4CAF50', '#FF9800', '#F44336'];

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_users: 0,
    approved_members: 0,
    pending_requests: 0,
    trusted_sources: 0
  });



  const [topMembersVotes, setTopMembersVotes] = useState([]); // ✅ replaced static data with state
  const [loading, setLoading] = useState(true);




 const [tweetVerificationData, setTweetVerificationData] = useState([
    { name: 'Verified', value: 0 },
    { name: 'Unverified', value: 0 },
    { name: 'False', value: 0 },
  ]);

  useEffect(() => {
  const fetchTweetData = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/admin/tweetdata");

      // Backend already returns the correct structure
      setTweetVerificationData(response.data);

    } catch (err) {
      console.error("Error fetching tweet verification stats:", err);
    }
  };

  fetchTweetData();
}, []);



  

  // ✅ Fetch stats data
  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const res = await axios.get('http://127.0.0.1:8000/admin/numbers');
        setStats(res.data);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardStats();
  }, []);

  // ✅ Fetch top 5 members data from backend
  useEffect(() => {
    const fetchTopMembers = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/admin/top-members');
        setTopMembersVotes(response.data);
      } catch (error) {
        console.error('Error fetching top members data:', error);
      }
    };

    fetchTopMembers();
  }, []);

  // ✅ Summary cards
  const summaryStats = [
    {
      title: 'Total Users',
      value: stats.total_users.toLocaleString(),
      icon: FiUsers,
      color: '#007bff',
      bgColor: 'rgba(0, 123, 255, 0.1)'
    },
    {
      title: 'Approved Members',
      value: stats.approved_members.toLocaleString(),
      icon: FiUserCheck,
      color: '#28a745',
      bgColor: 'rgba(40, 167, 69, 0.1)'
    },
    {
      title: 'Pending Requests',
      value: stats.pending_requests.toLocaleString(),
      icon: FiUserPlus,
      color: '#fd7e14',
      bgColor: 'rgba(253, 126, 20, 0.1)'
    },
    {
      title: 'Trusted Sources',
      value: stats.trusted_sources.toLocaleString(),
      icon: FiShield,
      color: '#6f42c1',
      bgColor: 'rgba(111, 66, 193, 0.1)'
    }
  ];

  // ✅ Example static recent activity
  const recentActivityData = [
   {
  title: 'Top Contributor',
  count: topMembersVotes?.[0]?.name || 0,
  subtitle: topMembersVotes?.[0]?.name || '',
  icon: FiUserPlus,
  color: '#fd7e14'
},
    { title: 'Verified Tweets Today', count: 89, icon: FiFileText, color: '#28a745' },
    { title: 'Members Votes Today', count: 450, icon: FiUsers, color: '#007bff' }
  ];

  return (
    <div className="dashboard-container">

    <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Admin Dashboard</h1>
          <p className="dashboard-subtitle">Welcome back</p>
        </div>
        <div className="user-profile">
          <div className="user-avatar">SJ</div>
          <div className="user-info">
            <p className="user-name"> Osama Ali</p>
            <p className="user-role">Admin</p>
          </div>
        </div>
      </div>

      {/* 🔹 Top Summary Cards */}
      <div className="stats-grid">
        {summaryStats.map((stat, index) => (
          <div key={index} className="stat-card">
            <div
              className="stat-icon"
              style={{ backgroundColor: stat.bgColor, color: stat.color }}
            >
              <stat.icon />
            </div>
            <div className="stat-info">
              <h3 className="stat-title">{stat.title}</h3>
              <p className="stat-value">{loading ? 'Loading...' : stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* 🔹 Main Dashboard Grid */}
      <div className="dashboard-main-grid">
        {/* 🔹 Bar Chart for Top 5 Members */}
        <div className="dashboard-card">
      <h2 className="card-header">Tweet Verification Status</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={tweetVerificationData}
          margin={{ top: 10, right: 30, left: 0, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip 
            formatter={(value) => [`${value} tweets`, 'Count']}
            labelStyle={{ fontWeight: 'bold' }}
          />
          <Legend />
          <Bar
            dataKey="value"
            radius={[8, 8, 0, 0]}
            barSize={45}
          >
            {tweetVerificationData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>

        {/* 🔹 Recent Activity */}
        <div className="dashboard-card">
          <h2 className="card-header">Recent Activity</h2>
          <div className="activity-list">
            {recentActivityData.map((item, index) => (
              <div key={index} className="activity-item">
                <div
                  className="activity-icon"
                  style={{ color: item.color, backgroundColor: `${item.color}1a` }}
                >
                  <item.icon />
                </div>
                <div className="activity-info">
                  <div className="title">{item.title}</div>
                  <div className="count">{item.count.toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
