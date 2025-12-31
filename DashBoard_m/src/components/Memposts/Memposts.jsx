// import React, { useEffect, useState } from 'react';
// import axios from 'axios';
// import './Memposts.css';
// import { useMember } from '../Auth/MemberContext';

// const Memposts = () => {
//   const { member } = useMember();
//   const [tweets, setTweets] = useState([]);
//   const [selectedTweet, setSelectedTweet] = useState(null);
//   const [votedTweets, setVotedTweets] = useState({});
//   const [sourceInputs, setSourceInputs] = useState({});
//   const [showUrlInput, setShowUrlInput] = useState({});

//   useEffect(() => {
//     axios.get('http://127.0.0.1:8000/member/tweets')
//       .then(res => setTweets(res.data))
//       .catch(err => console.error('Failed to load tweets', err));
//   }, []);

//   // 🟡 Simulate vote submission locally
//   const handleVote = (tweetId, voteValue) => {
//     setVotedTweets(prev => ({ ...prev, [tweetId]: `fake_vote_id_${tweetId}` }));
//     alert(`Vote (${voteValue ? "Verify" : "Unverify"}) submitted `);
//     setSelectedTweet(null);
//   };

//   // 🟡 Simulate source submission locally
//   const handleSubmitSources = (tweetId) => {
//     const sources = sourceInputs[tweetId] || [];
//     const validSources = sources.filter(url => url.trim() !== "");

//     if (!votedTweets[tweetId]) {
//       alert("Please vote before adding sources.");
//       return;
//     }

//     if (validSources.length === 0) {
//       alert("Please enter at least one source.");
//       return;
//     }

//     console.log(`Sources submitted for ${tweetId}:`, validSources);
//     alert('Sources submitted !');
//     setShowUrlInput(prev => ({ ...prev, [tweetId]: false }));
//   };

//   const updateSourceInput = (tweetId, index, value) => {
//     setSourceInputs(prev => ({
//       ...prev,
//       [tweetId]: [
//         ...(prev[tweetId] || []).map((val, i) => i === index ? value : val),
//         ...(prev[tweetId]?.length < 2 ? Array(2 - (prev[tweetId]?.length || 0)).fill('') : [])
//       ]
//     }));
//   };

//   return (
//     <div className="tweet-container">
//       <h1 className="heading">Vote on Posts</h1>
//       <div className="tweet-row">
//         {tweets.map(tweet => (
//           <div className="tweet-box" key={tweet.tweet_id}>
//             <div className="tweet-content-scroll">
//               <p>{tweet.content}</p>
//             </div>
//             <div className='action-buttons'>
//               <button
//                 className="vote-popup-btn"
//                 onClick={() => setSelectedTweet(tweet.tweet_id)}
//                 disabled={!!votedTweets[tweet.tweet_id]}
//               >
//                 {votedTweets[tweet.tweet_id] ? 'Voted' : 'Vote'}
//               </button>

//               <button
//                 className="add-url-btn"
//                 onClick={() => setShowUrlInput(prev => ({
//                   ...prev,
//                   [tweet.tweet_id]: !prev[tweet.tweet_id]
//                 }))}
//               >
//                 Add Sources
//               </button>
//             </div>

//             {showUrlInput[tweet.tweet_id] && (
//               <div className="source-inputs">
//                 <input
//                   type="url"
//                   placeholder="Source URL 1"
//                   value={sourceInputs[tweet.tweet_id]?.[0] || ''}
//                   onChange={(e) => updateSourceInput(tweet.tweet_id, 0, e.target.value)}
//                   disabled={!votedTweets[tweet.tweet_id]}
//                 />
//                 <input
//                   type="url"
//                   placeholder="Source URL 2"
//                   value={sourceInputs[tweet.tweet_id]?.[1] || ''}
//                   onChange={(e) => updateSourceInput(tweet.tweet_id, 1, e.target.value)}
//                   disabled={!votedTweets[tweet.tweet_id]}
//                 />
//                 <button
//                   onClick={() => handleSubmitSources(tweet.tweet_id)}
//                   disabled={!votedTweets[tweet.tweet_id]}
//                 >
//                   Submit Sources
//                 </button>
//               </div>
//             )}
//           </div>
//         ))}
//       </div>

//       {selectedTweet && (
//         <div className="modal">
//           <div className="modal-content">
//             <h3>Vote on Post</h3>
//             <div className="vote-buttons">
//               <button onClick={() => handleVote(selectedTweet, true)}>Verify</button>
//               <button onClick={() => handleVote(selectedTweet, false)}>Unverify</button>
//             </div>
//             <button className="close-btn" onClick={() => setSelectedTweet(null)}>Close</button>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default Memposts;













// import React, { useEffect, useState } from 'react';
// import axios from 'axios';
// import './Memposts.css';
// import { useMember } from '../Auth/MemberContext';

// const Memposts = () => {
//   const { member } = useMember();
//   const [tweets, setTweets] = useState([]);
//   const [selectedTweet, setSelectedTweet] = useState(null);
//   const [votedTweets, setVotedTweets] = useState({});
//   const [sourceInputs, setSourceInputs] = useState({});
//   const [showUrlInput, setShowUrlInput] = useState({});
//   const [sourcesSubmitted, setSourcesSubmitted] = useState({});

//   useEffect(() => {
//     axios.get('http://127.0.0.1:8000/member/tweets')
//       .then(res => setTweets(res.data))
//       .catch(err => console.error('Failed to load tweets', err));
//   }, []);

//   // 🟡 Simulate source submission locally
//   const handleSubmitSources = (tweetId) => {
//     const sources = sourceInputs[tweetId] || [];
//     const validSources = sources.filter(url => url.trim() !== "");

//     if (validSources.length === 0) {
//       alert("Please enter at least one source.");
//       return;
//     }

//     console.log(`Sources submitted for ${tweetId}:`, validSources);
//     alert('Sources submitted! You can now vote.');
    
//     // Mark that sources have been submitted for this tweet
//     setSourcesSubmitted(prev => ({ ...prev, [tweetId]: true }));
//     setShowUrlInput(prev => ({ ...prev, [tweetId]: false }));
//   };

//   // 🟡 Simulate vote submission locally (now requires sources first)
//   const handleVote = (tweetId, voteValue) => {
//     // Check if sources were submitted first
//     if (!sourcesSubmitted[tweetId]) {
//       alert("Please add and submit sources before voting.");
//       return;
//     }

//     setVotedTweets(prev => ({ ...prev, [tweetId]: `fake_vote_id_${tweetId}` }));
//     alert(`Vote (${voteValue ? "Verify" : "Unverify"}) submitted `);
//     setSelectedTweet(null);
//   };

//   const updateSourceInput = (tweetId, index, value) => {
//     setSourceInputs(prev => ({
//       ...prev,
//       [tweetId]: [
//         ...(prev[tweetId] || []).map((val, i) => i === index ? value : val),
//         ...(prev[tweetId]?.length < 2 ? Array(2 - (prev[tweetId]?.length || 0)).fill('') : [])
//       ]
//     }));
//   };

//   return (
//     <div className="tweet-container">
//       <h1 className="heading">Vote on Posts</h1>
//       <div className="tweet-row">
//         {tweets.map(tweet => (
//           <div className="tweet-box" key={tweet.tweet_id}>
//             <div className="tweet-content-scroll">
//               <p>{tweet.content}</p>
//             </div>
            
//             {/* Show Add Sources button first */}
//             <div className='action-buttons'>
//               <button
//                 className="add-url-btn"
//                 onClick={() => setShowUrlInput(prev => ({
//                   ...prev,
//                   [tweet.tweet_id]: !prev[tweet.tweet_id]
//                 }))}
//                 disabled={sourcesSubmitted[tweet.tweet_id] || votedTweets[tweet.tweet_id]}
//               >
//                 {sourcesSubmitted[tweet.tweet_id] ? 'Sources Added' : 'Add Sources'}
//               </button>

//               <button
//                 className="vote-popup-btn"
//                 onClick={() => setSelectedTweet(tweet.tweet_id)}
//                 disabled={!sourcesSubmitted[tweet.tweet_id] || !!votedTweets[tweet.tweet_id]}
//               >
//                 {votedTweets[tweet.tweet_id] ? 'Voted' : 
//                  sourcesSubmitted[tweet.tweet_id] ? 'Vote' : 'Add Sources First'}
//               </button>
//             </div>

//             {/* Source inputs - show when Add Sources is clicked */}
//             {showUrlInput[tweet.tweet_id] && (
//               <div className="source-inputs">
//                 <p className="source-instruction">Add at least one source before voting:</p>
//                 <input
//                   type="url"
//                   placeholder="Source URL 1"
//                   value={sourceInputs[tweet.tweet_id]?.[0] || ''}
//                   onChange={(e) => updateSourceInput(tweet.tweet_id, 0, e.target.value)}
//                 />
//                 <input
//                   type="url"
//                   placeholder="Source URL 2"
//                   value={sourceInputs[tweet.tweet_id]?.[1] || ''}
//                   onChange={(e) => updateSourceInput(tweet.tweet_id, 1, e.target.value)}
//                 />
//                 <button
//                   onClick={() => handleSubmitSources(tweet.tweet_id)}
//                 >
//                   Submit Sources
//                 </button>
//               </div>
//             )}
//           </div>
//         ))}
//       </div>

//       {/* Vote modal - only accessible after sources are submitted */}
//       {selectedTweet && sourcesSubmitted[selectedTweet] && (
//         <div className="modal">
//           <div className="modal-content">
//             <h3>Vote on Post</h3>
//             <p className="vote-instruction">You've submitted sources. Now cast your vote:</p>
//             <div className="vote-buttons">
//               <button onClick={() => handleVote(selectedTweet, true)}>Verify</button>
//               <button onClick={() => handleVote(selectedTweet, false)}>Unverify</button>
//             </div>
//             <button className="close-btn" onClick={() => setSelectedTweet(null)}>Close</button>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default Memposts;







import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './Memposts.css';
import { useMember } from '../Auth/MemberContext';

const Memposts = () => {
  const { member } = useMember();
  const [tweets, setTweets] = useState([]);
  const [selectedTweet, setSelectedTweet] = useState(null);
  const [votedTweets, setVotedTweets] = useState({});
  const [sourceInputs, setSourceInputs] = useState({});
  const [showUrlInput, setShowUrlInput] = useState({});
  const [sourcesSubmitted, setSourcesSubmitted] = useState({});
  const [loading, setLoading] = useState({});

  useEffect(() => {
    axios.get(`http://127.0.0.1:8000/member/tweets/${member.id}`)
      .then(res => setTweets(res.data))
      .catch(err => console.error('Failed to load tweets', err));
  }, [member?.id]);

  // ✅ Send vote and sources together
  const handleVoteAndSources = async (tweetId, voteValue) => {
    if (!member?.id) {
      alert("Please log in to vote.");
      return;
    }

    const sources = sourceInputs[tweetId] || [];
    const validSources = sources.filter(url => url.trim() !== "");

    if (validSources.length === 0) {
      alert("Please enter at least one source before voting.");
      return;
    }

    setLoading(prev => ({ ...prev, [tweetId]: true }));

    try {
      // Step 1: Create the vote
      const voteResponse = await axios.post('http://127.0.0.1:8000/member/vote', {
        tweet_id: tweetId,
        user_id: member.id,
        vote: voteValue  // ✅ Send actual vote value (true/false)
      });

      const voteId = voteResponse.data.vote_id;

      // Step 2: Add sources for this vote
      if (validSources.length > 0) {
        await Promise.all(
          validSources.map(sourceUrl => 
            axios.post('http://127.0.0.1:8000/member/vote_sources', {
              vote_id: voteId,
              source_url: sourceUrl
            })
          )
        );
      }

      alert(`Vote (${voteValue ? "Verify" : "Unverify"}) and sources submitted successfully!`);
      
      // Update local state
      setVotedTweets(prev => ({ ...prev, [tweetId]: voteId }));
      setSourcesSubmitted(prev => ({ ...prev, [tweetId]: true }));
      setShowUrlInput(prev => ({ ...prev, [tweetId]: false }));
      setSelectedTweet(null);
      
    } catch (error) {
      console.error('Failed to submit vote and sources:', error);
      if (error.response?.status === 400) {
        alert("You have already voted on this tweet.");
      } else {
        alert(error.response?.data?.detail || 'Failed to submit vote and sources');
      }
    } finally {
      setLoading(prev => ({ ...prev, [tweetId]: false }));
    }
  };

  // ✅ Updated vote handler (now includes sources)
  const handleVote = async (tweetId, voteValue) => {
    await handleVoteAndSources(tweetId, voteValue);
  };

  // ✅ Keep sources collection separate
  const handleSubmitSources = (tweetId) => {
    const sources = sourceInputs[tweetId] || [];
    const validSources = sources.filter(url => url.trim() !== "");

    if (validSources.length === 0) {
      alert("Please enter at least one source.");
      return;
    }

    // Just mark sources as ready, don't send to backend yet
    alert('Sources ready! Click Vote to submit both sources and your vote.');
    setSourcesSubmitted(prev => ({ ...prev, [tweetId]: true }));
    setShowUrlInput(prev => ({ ...prev, [tweetId]: false }));
  };

  const updateSourceInput = (tweetId, index, value) => {
    setSourceInputs(prev => ({
      ...prev,
      [tweetId]: [
        ...(prev[tweetId] || []).map((val, i) => i === index ? value : val),
        ...(prev[tweetId]?.length < 2 ? Array(2 - (prev[tweetId]?.length || 0)).fill('') : [])
      ]
    }));
  };

  return (
    <div className="tweet-container">
      <h1 className="heading">Vote on Posts</h1>
      {!member?.id && (
        <div className="login-warning">
          Please log in to add sources and vote.
        </div>
      )}
      <div className="tweet-row">
        {tweets.map(tweet => (
          <div className="tweet-box" key={tweet.tweet_id}>
            <div className="tweet-content-scroll">
              <p>{tweet.tweet_text || tweet.content}</p>
            </div>
            
            <div className='action-buttons'>
              <button
                className="add-url-btn"
                onClick={() => setShowUrlInput(prev => ({
                  ...prev,
                  [tweet.tweet_id]: !prev[tweet.tweet_id]
                }))}
                disabled={sourcesSubmitted[tweet.tweet_id] || votedTweets[tweet.tweet_id] || !member?.id}
              >
                {sourcesSubmitted[tweet.tweet_id] ? 'Sources Ready' : 'Add Sources'}
              </button>

              <button
                className="vote-popup-btn"
                onClick={() => setSelectedTweet(tweet.tweet_id)}
                disabled={!sourcesSubmitted[tweet.tweet_id] || !!votedTweets[tweet.tweet_id] || !member?.id}
              >
                {votedTweets[tweet.tweet_id] ? 'Voted' : 
                 sourcesSubmitted[tweet.tweet_id] ? 'Vote' : 'Add Sources First'}
              </button>
            </div>

            {showUrlInput[tweet.tweet_id] && (
              <div className="source-inputs">
                <p className="source-instruction">Add sources before voting:</p>
                <input
                  type="url"
                  placeholder="Source URL 1"
                  value={sourceInputs[tweet.tweet_id]?.[0] || ''}
                  onChange={(e) => updateSourceInput(tweet.tweet_id, 0, e.target.value)}
                />
                <input
                  type="url"
                  placeholder="Source URL 2"
                  value={sourceInputs[tweet.tweet_id]?.[1] || ''}
                  onChange={(e) => updateSourceInput(tweet.tweet_id, 1, e.target.value)}
                />
                <button
                  onClick={() => handleSubmitSources(tweet.tweet_id)}
                >
                  Save Sources
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {selectedTweet && sourcesSubmitted[selectedTweet] && (
        <div className="modal">
          <div className="modal-content">
            <h3>Vote on Post</h3>
            <p className="vote-instruction">Submit your vote and sources:</p>
            <div className="vote-buttons">
              <button 
                onClick={() => handleVote(selectedTweet, true)}
                disabled={loading[selectedTweet]}
              >
                {loading[selectedTweet] ? 'Submitting...' : 'Verify'}
              </button>
              <button 
                onClick={() => handleVote(selectedTweet, false)}
                disabled={loading[selectedTweet]}
              >
                {loading[selectedTweet] ? 'Submitting...' : 'Unverify'}
              </button>
            </div>
            <button className="close-btn" onClick={() => setSelectedTweet(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Memposts;