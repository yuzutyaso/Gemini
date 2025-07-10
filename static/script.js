document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatBox = document.getElementById('chat-box');

    // メッセージをチャットボックスに追加する関数
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(`${sender}-message`); // 'user-message' または 'ai-message'
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // 新しいメッセージが追加されたらスクロールを一番下へ
    }

    // メッセージ送信処理
    async function sendMessage() {
        const message = userInput.value.trim(); // 入力値の前後空白を削除
        if (message === '') { // メッセージが空の場合は何もしない
            return;
        }

        addMessage(message, 'user'); // ユーザーのメッセージをチャットボックスに表示
        userInput.value = ''; // 入力フィールドをクリア

        try {
            // FastAPIのバックエンド（/chatエンドポイント）にPOSTリクエストを送信
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json' // JSON形式でデータを送信
                },
                body: JSON.stringify({ message: message }) // メッセージをJSON形式でボディに含める
            });

            if (!response.ok) { // HTTPステータスコードが200番台以外の場合
                const errorData = await response.json(); // エラーレスポンスをJSONとして解析
                throw new Error(errorData.detail || 'APIリクエストに失敗しました');
            }

            const data = await response.json(); // 成功レスポンスをJSONとして解析
            addMessage(data.response, 'ai'); // AIの応答をチャットボックスに表示

        } catch (error) {
            console.error('チャットエラー:', error);
            addMessage('エラー: メッセージを送信できませんでした。', 'ai'); // エラーメッセージを表示
        }
    }

    // 送信ボタンがクリックされたらsendMessage関数を実行
    sendButton.addEventListener('click', sendMessage);

    // ユーザーがEnterキーを押したらsendMessage関数を実行
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
