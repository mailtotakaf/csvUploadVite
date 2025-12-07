<!-- src/App.vue -->
<template>
  <div class="container">
    <h1>CSV アップロード</h1>

    <div class="card">
      <label class="file-label">
        CSVファイルを選択:
        <input type="file" accept=".csv" @change="onFileChange" />
      </label>

      <button
        class="btn"
        @click="upload"
        :disabled="uploading || !file"
      >
        {{ uploading ? 'アップロード中...' : 'アップロード' }}
      </button>

      <p class="status">
        {{ status }}
      </p>

      <div v-if="lastKey" class="result">
        <h3>直近アップロード:</h3>
        <p>{{ lastKey }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Viteの環境変数は import.meta.env に入る
const apiUrl = import.meta.env.VITE_API_ENDPOINT;

const file = ref(null);
const status = ref('');
const uploading = ref(false);
const lastKey = ref('');

const onFileChange = (e) => {
  const files = e.target.files;
  if (!files || !files.length) {
    file.value = null;
    status.value = 'ファイルが選択されていません';
    return;
  }
  file.value = files[0];
  status.value = `選択中: ${file.value.name}`;
};

const upload = async () => {
  if (!file.value) {
    status.value = 'CSVファイルを選択してください';
    return;
  }
  if (!apiUrl) {
    status.value = 'API エンドポイントが設定されていません (VITE_API_ENDPOINT)';
    return;
  }

  uploading.value = true;
  status.value = 'アップロード中...';

  try {
    const text = await file.value.text();

    const res = await fetch(apiUrl, {
      method: 'POST',
      // CORS簡略化のためヘッダは付けない（Lambda側でOKな形式）
      body: text,
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    status.value = `アップロード完了。登録件数: ${data.item_count}`;
    lastKey.value = data.key || JSON.stringify(data);
  } catch (err) {
    console.error(err);
    status.value = 'エラー: ' + err;
  } finally {
    uploading.value = false;
  }
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: 40px auto;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  padding: 0 16px;
}

h1 {
  font-size: 24px;
  margin-bottom: 24px;
}

.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
}

.file-label {
  display: block;
  margin-bottom: 12px;
}

.btn {
  margin-top: 8px;
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status {
  margin-top: 12px;
  min-height: 1.5em;
}

.result {
  margin-top: 16px;
  padding: 8px;
  background: #f3f4f6;
  border-radius: 4px;
}
</style>
