import React, { useState, useEffect } from 'react';
import { Layout, Card, Typography, Switch, Tabs } from 'antd';
import { MoonOutlined, SunOutlined } from '@ant-design/icons';
import axios from 'axios';
import CoffeeChat from './components/CoffeeChat';

const { Header, Content } = Layout;
const { Title } = Typography;

function App() {
  const [coffeeTypes, setCoffeeTypes] = useState([]);
  const [darkMode, setDarkMode] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme === 'dark';
  });

  useEffect(() => {
    const fetchCoffeeInfo = async () => {
      try {
        const response = await axios.get('http://localhost:5001/api/coffee/info');
        setCoffeeTypes(response.data.coffee_types);
      } catch (error) {
        console.error('Error fetching coffee info:', error);
      }
    };

    fetchCoffeeInfo();
  }, []);

  useEffect(() => {
    document.body.style.backgroundColor = darkMode ? '#141414' : '#fff';
    localStorage.setItem('theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  const handleThemeChange = (checked) => {
    setDarkMode(checked);
  };

  const items = [
    {
      key: '1',
      label: '咖啡豆介绍',
      children: (
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          {coffeeTypes.map((coffee, index) => (
            <Card 
              key={index} 
              title={coffee.name} 
              style={{ 
                width: 300,
                backgroundColor: darkMode ? '#1f1f1f' : '#fff',
                color: darkMode ? '#fff' : 'rgba(0, 0, 0, 0.85)',
                borderColor: darkMode ? '#303030' : '#f0f0f0'
              }}
              headStyle={{
                backgroundColor: darkMode ? '#1f1f1f' : '#fff',
                color: darkMode ? '#fff' : 'rgba(0, 0, 0, 0.85)',
                borderColor: darkMode ? '#303030' : '#f0f0f0'
              }}
            >
              <p style={{ color: darkMode ? '#fff' : 'rgba(0, 0, 0, 0.85)' }}>
                {coffee.description}
              </p>
            </Card>
          ))}
        </div>
      ),
    },
    {
      key: '2',
      label: '咖啡顾问',
      children: <CoffeeChat darkMode={darkMode} />,
    },
  ];

  return (
    <Layout style={{ 
      minHeight: '100vh',
      backgroundColor: darkMode ? '#141414' : '#fff'
    }}>
      <Header style={{ 
        background: darkMode ? '#1f1f1f' : '#fff', 
        padding: '0 20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Title level={2} style={{ 
          margin: '16px 0',
          color: darkMode ? '#fff' : 'rgba(0, 0, 0, 0.85)'
        }}>
          咖啡豆机器人
        </Title>
        <Switch
          checked={darkMode}
          onChange={handleThemeChange}
          checkedChildren={<MoonOutlined />}
          unCheckedChildren={<SunOutlined />}
        />
      </Header>
      <Content style={{ padding: '20px' }}>
        <Tabs 
          items={items}
          style={{
            color: darkMode ? '#fff' : 'rgba(0, 0, 0, 0.85)'
          }}
        />
      </Content>
    </Layout>
  );
}

export default App; 