import React, { useEffect, useState } from "react";
import "./Memactivity.css";
import { useMember } from '../Auth/MemberContext';
import axios from "axios"; // Uncommented axios

const MyActivity = () => {
  const [activityData, setActivityData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { member } = useMember();

  useEffect(() => {
    const fetchActivityData = async () => {
      setLoading(true);
      setError(null);

      if (!member?.id) {
        setError("No member ID found. Please log in.");
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`http://127.0.0.1:8000/member/activity/${member.id}`);
        
        // Assuming the API returns data in the expected format
        setActivityData(response.data);
      } catch (err) {
        console.error("Error fetching activity data:", err);
        setError("Failed to load your activity. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchActivityData();
  }, [member]);

  return (
    <div className="activity-container">
      <h2 className="heading">My Activity</h2>

      {loading ? (
        <p className="no-activity">Loading activity...</p>
      ) : error ? (
        <p className="no-activity">{error}</p>
      ) : activityData.length === 0 ? (
        <p className="no-activity">You haven't voted or added any sources yet.</p>
      ) : (
        <div className="activity-grid">
          {activityData.map((item) => (
            <div className="activity-card" key={item.id}>
              <div className="activity-post-content">{item.postContent}</div>

              <div className="vote-section">
                <span
                  className={`vote-tag ${
                    item.userVote === "True" ? "vote-true" : "vote-false"
                  }`}
                >
                  {item.userVote === "True" ? "✅ Marked True" : "❌ Marked False"}
                </span>
              </div>

              <div className="sources-section">
                <h4>Sources Added:</h4>
                {item.addedSources && item.addedSources.length > 0 ? (
                  <ul>
                    {item.addedSources.map((src, index) => (
                      <li key={index}>
                        <a href={src} target="_blank" rel="noreferrer">
                          {src}
                        </a>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="no-source">No sources added for this post.</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyActivity;