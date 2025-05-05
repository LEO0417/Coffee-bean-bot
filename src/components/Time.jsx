import React from 'react';
import { BiTime } from 'react-icons/bi';
import './Time.css';

const Time = () => {
  const [currentTime, setCurrentTime] = React.useState(new Date().toLocaleTimeString());

  React.useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="time-display">
      <BiTime className="clock-icon" />
      <span>{currentTime}</span>
    </div>
  );
};

export default Time; 