
import './member_dash.css';
import axios from 'axios';
import { useMember } from '../Auth/MemberContext';
import React, { useState, useEffect } from 'react';




function MemberDashboard() {


  const { member } = useMember();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [accuracyScore, setAccuracyScore] = useState(0);
const [loadingAccuracy, setLoadingAccuracy] = useState(false);
  
  const [contributions, setContributions] = useState({
    totalVotes: 0,
    totalSources: 0,

    username : '',
    streak:0

  });


  // Add these state variables at the top of your component


// The useEffect hook
// The useEffect hook
useEffect(() => {
  const fetchMemberAccuracy = async () => {
    try {
      if (!member?.id) return;
      
      setLoadingAccuracy(true);
      const response = await axios.get(
        `http://127.0.0.1:8000/member/accuracy/${member.id}`  // Updated route path
      );
      
      // Set the accuracy score from backend response
      // Now using response.data.accuracy instead of response.data.accuracy_percentage
      setAccuracyScore(response.data.accuracy);
      
    } catch (err) {
      console.error('Failed to fetch accuracy data:', err);
      // Fallback to 0 if there's an error
      setAccuracyScore(0);
    } finally {
      setLoadingAccuracy(false);
    }
  };

  fetchMemberAccuracy();
}, [member?.id]);


  useEffect(() => {
    const fetchContributions = async () => {
      try {
        if (!member?.id) return;
        
        setLoading(true);
        const response = await axios.get(`http://127.0.0.1:8000/member/contributions/${member.id}`);
        
        setContributions({
          totalVotes: response.data.total_votes || 0,
          totalSources: response.data.total_sources || 0,
          username: response.data.username || '' ,
          streak: response.data.current_streak || 0
 
          
        });
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err.response?.data?.message || 'Failed to fetch contribution data');
      } finally {
        setLoading(false);
      }
    };

    fetchContributions();
  }, [member?.id]);



  const stats = [
    {
      title: 'Total Votes Cast',
      value: contributions.totalVotes.toLocaleString(),
      
      icon: '🗳️',
      color: 'blue'
    },
    {
      title: 'Sources Added',
      value: contributions.totalSources.toLocaleString(),
      
      icon: '📚',
      color: 'cyan'
    },
   
    {
      title: 'Accuracy Meter',
      value: accuracyScore,
    
      icon: '📈',
      color: 'blue'
    }
  ];



  //  useEffect(() => {
  //   const fetchVotesOverTime = async () => {
  //     try {
  //       if (!member?.id) return;
        
  //       setLoading(true);
  //       const response = await axios.get(
  //         `http://127.0.0.1:8000/member/votes-over-time/${member.id}`
  //       );
        
  //       // Transform the data for the chart
  //       const transformedData = response.data.map(item => ({
  //         day: item.date,
  //         value: item.votes
  //       }));
        
  //       setChartData(transformedData);
  //     } catch (err) {
  //       console.error('Failed to fetch vote data:', err);
  //       // Fallback to empty data
  //       setChartData(Array(10).fill(0).map((_, i) => ({
  //         day: `Day ${i+1}`,
  //         value: 0
  //       })));
  //     } finally {
  //       setLoading(false);
  //     }
  //   };

  //   fetchVotesOverTime();
  // }, [member?.id]);




  useEffect(() => {
  const fetchVotesOverTime = async () => {
    try {
      if (!member?.id) return;
      
      setLoading(true);
      const response = await axios.get(
        `http://127.0.0.1:8000/member/votes-over-time/${member.id}`
      );
      
      // Transform the data for the chart
      const transformedData = response.data.map(item => ({
        day: item.date,
        value: item.votes
      }));
      
      setChartData(transformedData);
    } catch (err) {
      console.error('Failed to fetch vote data:', err);
      // Fallback to empty data
      setChartData(Array(10).fill(0).map((_, i) => ({
        day: `Day ${i+1}`,
        value: 0
      })));
    } finally {
      setLoading(false);
    }
  };

  fetchVotesOverTime();
}, [member?.id]);

// Calculate max value for Y-axis scaling
const maxValue = Math.max(...chartData.map(d => d.value), 1);
const yAxisLabels = [0, Math.ceil(maxValue * 0.25), Math.ceil(maxValue * 0.5), Math.ceil(maxValue * 0.75), Math.ceil(maxValue)];










  const barData = [
    { label: 'News Sites', value: 450 },
    { label: 'Govt Sources', value: 320 },
    { label: 'Research', value: 280 },
    { label: 'Fact-Check', value: 180 },
    { label: 'Academic', value: 120 }
  ];

  const platformData = [
    { name: 'Twitter', value: 45, color: '#4DA8DA' },
    { name: 'Facebook', value: 30, color: '#F472B6' },
    { name: 'Instagram', value: 20, color: '#8B5CF6' },
    { name: 'Others', value: 5, color: '#F59E0B' }
  ];

  const maxBarValue = Math.max(...barData.map(d => d.value));

  return (
    <main className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Member Dashboard</h1>
          <p className="dashboard-subtitle">Welcome back, Track your post verification activity</p>
        </div>
        <div className="user-profile">
          <div className="user-avatar">SJ</div>
          <div className="user-info">
            <p className="user-name">  {contributions.username || member?.username || 'Member'}</p>
            <p className="user-role">Active Member</p>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className={`stat-card stat-${stat.color}`}>
            <div className="stat-header">
              <span className="stat-icon">{stat.icon}</span>
              <span className="stat-menu">⋮</span>
            </div>
            <p className="stat-title">{stat.title}</p>
            <h2 className="stat-value">{stat.value}</h2>
            <p className="stat-trend">
              <span className="trend-arrow">↑</span> {stat.trend}
            </p>
          </div>
        ))}
      </div>

      <div className="charts-section">
       

      <div className="chart-card line-chart-card">
    <div className="chart-header">
      <h3 className="chart-title">Votes Cast Over Time</h3>
      <div className="chart-controls">
        <button className="chart-btn active">10 Days</button>
      </div>
    </div>
    
    {loading ? (
      <div className="chart-loading">Loading vote data...</div>
    ) : (
      <div className="line-chart">
        <svg viewBox="0 0 650 200" className="chart-svg">
          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#6B5AED" />
              <stop offset="100%" stopColor="#4DA8DA" />
            </linearGradient>
            <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#6B5AED" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#6B5AED" stopOpacity="0" />
            </linearGradient>
          </defs>
          
          {/* Y-axis labels */}
          {yAxisLabels.map((label, i) => (
            <text
              key={i}
              x="25"
             y={170 - i * 35} 
              textAnchor="end"
              fontSize="10"
              fill="#64748B"
              fontWeight="500"
            >
              {label}
            </text>
          ))}
          
          {/* Grid lines */}
          {[0, 1, 2, 3, 4].map(i => (
            <line
              key={i}
              x1="40"
              y1={30 + i * 35}
              x2="590"
              y2={30 + i * 35}
              stroke="#E2E8F0"
              strokeWidth="1"
            />
          ))}

          {/* Line path */}
          <path
            d={`M ${chartData.map((d, i) => `${60 + i * 53},${180 - (d.value / maxValue) * 140}`).join(' L ')}`}
            fill="none"
            stroke="url(#lineGradient)"
            strokeWidth="3"
            strokeLinecap="round"
          />

          {/* Area fill */}
          <path
            d={`M 60,180 L ${chartData.map((d, i) => `${60 + i * 53},${180 - (d.value / maxValue) * 140}`).join(' L ')} L 590,180 Z`}
            fill="url(#areaGradient)"
          />

          {/* Data points */}
          {chartData.map((d, i) => (
            <circle
              key={i}
              cx={60 + i * 53}
              cy={180 - (d.value / maxValue) * 140}
              r="4"
              fill="#6B5AED"
            />
          ))}

          {/* X-axis labels */}
          {chartData.map((d, i) => (
            <text
              key={i}
              x={60 + i * 53}
              y="195"
              textAnchor="middle"
              fontSize="11"
              fill="#64748B"
            >
              {d.day}
            </text>
          ))}
        </svg>
      </div>
    )}
  </div>







        <div className="activity-summary">
          <div className="summary-header">
            <h3 className="summary-title">My Activity Summary</h3>
            <button className="summary-link"></button>
          </div>

          <div className="summary-stat">
            <div className="summary-label">
              <span className="summary-icon">✓</span>
              Votes Casted
            </div>
            <div className="summary-value">{contributions.totalVotes.toLocaleString()}</div>
          </div>

          <div className="summary-stat">
            <div className="summary-label">
              <span className="summary-icon">📅</span>
              Member Since
            </div>
            <div className="summary-value-small">Sep 2025</div>
          </div>

          <div className="summary-stat">
            <div className="summary-label">
              <span className="summary-icon">🔥</span>
              Current Streak
            </div>
            <div className="summary-value-small">{contributions.streak.toLocaleString()}</div>
          </div>

         
        </div>
      </div>

      
        

        
    </main>
  );
}

export default MemberDashboard;