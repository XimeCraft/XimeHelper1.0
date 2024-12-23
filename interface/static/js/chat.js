class ChatAPI {
    constructor() {
        this.endpoint = '/api/chat';
    }

    async sendMessage(message) {
        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }
}

class ChatUI {
    constructor() {
        this.chatAPI = new ChatAPI();
        this.chatForm = document.getElementById('chat-form');
        this.chatInput = document.getElementById('chat-input');
        this.messagesContainer = document.getElementById('chat-messages');
        this.messageTemplate = document.getElementById('message-template');

        this.setupEventListeners();
    }

    setupEventListeners() {
        // 自动调整输入框高度
        this.chatInput.addEventListener('input', () => this.adjustInputHeight());

        // 处理表单提交
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    adjustInputHeight() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = this.chatInput.scrollHeight + 'px';
    }

    async handleSubmit(e) {
        e.preventDefault();
        const message = this.chatInput.value.trim();
        if (!message) return;

        // 添加用户消息
        this.appendMessage(message, 'user');
        this.chatInput.value = '';
        this.chatInput.style.height = 'auto';

        try {
            // 发送消息到后端
            const response = await this.chatAPI.sendMessage(message);
            // 添加助手回复
            this.appendMessage(response.response, 'assistant');
        } catch (error) {
            this.appendMessage('Sorry, something went wrong. Please try again.', 'error');
        }
    }

    appendMessage(text, type) {
        const message = this.messageTemplate.content.cloneNode(true);
        const messageDiv = message.querySelector('.message');
        const messageText = message.querySelector('.message-text');

        messageDiv.classList.add(`message-${type}`);
        messageText.textContent = text;
        this.messagesContainer.appendChild(message);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

// 初始化聊天界面
document.addEventListener('DOMContentLoaded', () => {
    new ChatUI();
}); 