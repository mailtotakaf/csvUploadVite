<template>
  <div class="container">
    <h1>商品マスタ CSV アップロード & 一覧</h1>

    <!-- CSVアップロード -->
    <section class="card">
      <h2>CSV アップロード</h2>
      <p>store_id,product_id,product_name,price,image_key の形式のCSVをアップロードします。</p>

      <input type="file" accept=".csv" @change="onFileChange" />
      <button class="btn" @click="upload" :disabled="uploading || !file">
        {{ uploading ? 'アップロード中...' : 'アップロード' }}
      </button>

      <p class="status">{{ status }}</p>
      <p v-if="lastResult" class="status">
        {{ lastResult }}
      </p>
    </section>

    <!-- 商品一覧 -->
    <section class="card">
      <h2>商品一覧</h2>
      <div class="row">
        <label>
          store_id:
          <input v-model="storeId" placeholder="例: 101" />
        </label>
        <button class="btn" @click="loadProducts" :disabled="loadingList">
          {{ loadingList ? '読み込み中...' : '読み込み' }}
        </button>
      </div>

      <p class="status" v-if="listMessage">{{ listMessage }}</p>

      <table v-if="products.length" class="table">
        <thead>
          <tr>
            <th>store_id</th>
            <th>product_id</th>
            <th>商品名</th>
            <th>価格</th>
            <th>画像キー</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.store_id + ':' + p.product_id">
            <td>{{ p.store_id }}</td>
            <td>{{ p.product_id }}</td>
            <td>{{ p.product_name }}</td>
            <td>{{ p.price }}</td>
            <td>{{ p.image_key }}</td>
          </tr>
        </tbody>
      </table>

      <p v-else class="status">データがありません</p>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 環境変数から API のベースURLを取得
const apiBase = import.meta.env.VITE_API_BASE

const file = ref(null)
const status = ref('')
const uploading = ref(false)
const lastResult = ref('')

const storeId = ref('101')
const products = ref([])
const loadingList = ref(false)
const listMessage = ref('')

// ファイル選択
const onFileChange = (e) => {
  const files = e.target.files
  if (!files || !files.length) {
    file.value = null
    status.value = 'ファイルが選択されていません'
    return
  }
  file.value = files[0]
  status.value = `選択中: ${file.value.name}`
}

// アップロード
const upload = async () => {
  if (!file.value) {
    status.value = 'CSVファイルを選択してください'
    return
  }
  if (!apiBase) {
    status.value = 'VITE_API_BASE が設定されていません'
    return
  }

  uploading.value = true
  status.value = 'アップロード中...'
  lastResult.value = ''

  try {
    const text = await file.value.text()

    const res = await fetch(`${apiBase}/upload`, {
      method: 'POST',
      // CORSを簡単にするためヘッダは付けない
      body: text
    })

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`)
    }

    const data = await res.json()
    status.value = 'アップロード完了'
    lastResult.value = `登録件数: ${data.item_count ?? '-'} / CSVキー: ${data.csv_key ?? '-'}`

  } catch (err) {
    console.error(err)
    status.value = 'アップロードエラー'
    lastResult.value = String(err)
  } finally {
    uploading.value = false
  }
}

// 商品一覧取得
const loadProducts = async () => {
  if (!storeId.value) {
    listMessage.value = 'store_id を入力してください'
    return
  }
  if (!apiBase) {
    listMessage.value = 'VITE_API_BASE が設定されていません'
    return
  }

  loadingList.value = true
  listMessage.value = '読み込み中...'
  products.value = []

  try {
    const url = `${apiBase}/products?store_id=${encodeURIComponent(storeId.value)}`
    const res = await fetch(url)
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`)
    }
    const data = await res.json()
    products.value = data.items ?? []
    listMessage.value = `取得件数: ${products.value.length}`
  } catch (err) {
    console.error(err)
    listMessage.value = '取得エラー: ' + String(err)
  } finally {
    loadingList.value = false
  }
}
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 40px auto;
  padding: 0 16px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
h1 {
  font-size: 24px;
  margin-bottom: 24px;
}
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}
.btn {
  margin-left: 8px;
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  background: #2563eb;
  color: white;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.status {
  margin-top: 8px;
  min-height: 1.2em;
}
.row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  font-size: 14px;
}
.table th,
.table td {
  border: 1px solid #ddd;
  padding: 4px 8px;
}
.table th {
  background: #f3f4f6;
}
</style>
