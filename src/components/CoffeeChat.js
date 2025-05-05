import React, { useState } from 'react';
import { Input, Button, Card, Space, Select } from 'antd';
import axios from 'axios';

const { TextArea } = Input;

function CoffeeChat({ darkMode }) {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gpt-3.5-turbo');
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!question.trim() || !apiKey.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5001/api/chat', {
        message: question,
        api_key: apiKey,
        model: model
      });

      setMessages(prev => [...prev, 
        { role: 'user', content: question },
        { role: 'assistant', content: response.data.response }
      ]);
      setQuestion('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '20px' }}>
      <Card
        style={{
          marginBottom: 20,
          backgroundColor: darkMode ? '#1f1f1f' : '#fff',
          borderColor: darkMode ? '#303030' : '#f0f0f0'
        }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Input
            placeholder="输入你的 API Key"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            style={{
              backgroundColor: darkMode ? '#141414' : '#fff',
              color: darkMode ? '#fff' : '#000',
              borderColor: darkMode ? '#303030' : '#d9d9d9'
            }}
          />
          <Select
            value={model}
            onChange={value => setModel(value)}
            style={{ width: '100%' }}
            options={[
              { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
              { value: 'gpt-4', label: 'GPT-4' }
            ]}
          />
        </Space>
      </Card>

      <div style={{ 
        marginBottom: 20,
        maxHeight: '400px',
        overflowY: 'auto',
        padding: '10px',
        backgroundColor: darkMode ? '#1f1f1f' : '#f5f5f5',
        borderRadius: '8px'
      }}>
        {messages.map((msg, index) => (
          <Card
            key={index}
            style={{
              marginBottom: 10,
              backgroundColor: darkMode ? '#141414' : '#fff',
              borderColor: darkMode ? '#303030' : '#f0f0f0'
            }}
          >
            <p style={{ 
              margin: 0,
              color: darkMode ? '#fff' : '#000'
            }}>
              {msg.role === 'user' ? '问：' : '答：'} {msg.content}
            </p>
          </Card>
        ))}
      </div>

      <Space.Compact style={{ width: '100%' }}>
        <TextArea
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="输入你的问题..."
          autoSize={{ minRows: 2, maxRows: 6 }}
          style={{
            backgroundColor: darkMode ? '#141414' : '#fff',
            color: darkMode ? '#fff' : '#000',
            borderColor: darkMode ? '#303030' : '#d9d9d9'
          }}
        />
        <Button
          type="primary"
          onClick={handleSend}
          loading={loading}
          style={{ height: 'auto' }}
        >
          发送
        </Button>
      </Space.Compact>
    </div>
  );
}

export default CoffeeChat; 