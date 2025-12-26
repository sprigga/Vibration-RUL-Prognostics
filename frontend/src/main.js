import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 原始：僅導入 Element Plus 預設樣式
// 修改：導入 Element Plus 深色主題 CSS 變數
import 'element-plus/theme-chalk/dark/css-vars.css'
// 修改：導入全局深色主題樣式（Apple Keynote 漸層深色系）
import './styles/theme-dark.css'
// 修改：導入統一通用樣式（字體、文字、顏色等，參照 FONT.md）
import './styles/common-styles.css'
// 修改：導入 Element Plus 下拉選單深色主題全局樣式（解決下拉選單樣式問題）
import './styles/select-dropdown-dark.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
