document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatBox = document.getElementById('chat-box');

    // メッセージをチャットボックスに追加する関数
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(`${sender}-message`);
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // スクロールを一番下へ
    }

    // メッセージ送信処理
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') {
            return;
        }

        addMessage(message, 'user'); // ユーザーのメッセージを表示
        userInput.value = ''; // 入力フィールドをクリア

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'APIリクエストに失敗しました');
            }

            const data = await response.json();
            addMessage(data.response, 'ai'); // AIの応答を表示

        } catch (error) {
            console.error('チャットエラー:', error);
            addMessage('エラー: メッセージを送信できませんでした。', 'ai');
        }
    }

    // 送信ボタンのクリックイベント
    sendButton.addEventListener('click', sendMessage);

    // Enterキーでの送信イベント
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
