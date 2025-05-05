import React from 'react';
import { BiTime } from 'react-icons/bi';
import './Time.css';

const Time = ({ darkMode }) => {
  const [currentTime, setCurrentTime] = React.useState(new Date().toLocaleTimeString());
  const [currentDate, setCurrentDate] = React.useState(new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  }));

  React.useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString());
      setCurrentDate(now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      }));
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className={`time-container ${darkMode ? 'time-dark' : 'time-light'}`}>
      <div className="time-display">
        <BiTime className="clock-icon" />
        <span>{currentDate} {currentTime}</span>
      </div>
    </div>
  );
};

export default Time; 